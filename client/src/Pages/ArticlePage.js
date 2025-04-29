import React, { useEffect, useState } from "react";
import { useOutletContext, useParams } from "react-router-dom";

function ArticlePage() {
    const { user } = useOutletContext();
    const { id } = useParams();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [userMap, setUserMap] = useState({});
    const [newVote, setNewVote] = useState(true);
    const [votesMap, setVotesMap] = useState({});
    const [votableType, setVotableType] = useState("Article");


    const formatDate = (dateString) => {
        if (dateString.includes(' ')) {
            dateString = dateString.replace(' ', 'T') + 'Z';
        }

        const articleDate = new Date(dateString);

        if (isNaN(articleDate)) {
            console.error("Invalid date");
            return 'Invalid Date';
        }

        const now = new Date();

        const isToday =
            articleDate.getDate() === now.getDate() &&
            articleDate.getMonth() === now.getMonth() &&
            articleDate.getFullYear() === now.getFullYear();

        const isThisYear = articleDate.getFullYear() === now.getFullYear();

        const options = {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
        };

        if (!isToday) {
            options.month = 'numeric';
            options.day = 'numeric';
        }

        if (!isThisYear) {
            options.year = 'numeric';
        }

        return articleDate.toLocaleString('en-US', options);
    };

    useEffect(() => {
        async function fetchArticleAndUsers() {
            try {
                const response = await fetch(`/article/${id}`);
                const data = await response.json();
                if (data) {
                    setArticle(data);

                    const uniqueUserIds = [
                        ...new Set(data.comments.map(comment => comment.user_id).filter(Boolean))
                    ];

                    const userFetches = await Promise.all(
                        uniqueUserIds.map(uid =>
                            fetch(`/user/${uid}`)
                                .then(resp => resp.json())
                                .then(userData => ({ [uid]: userData }))
                                .catch(() => ({ [uid]: null })) // In case fetch fails
                        )
                    );

                    // Merge all objects into one map
                    const mergedUserMap = Object.assign({}, ...userFetches);
                    setUserMap(mergedUserMap);
                } else {
                    console.error("Error: Data is not in expected format", data);
                }
            } catch (error) {
                console.error("Error fetching article:", error);
            } finally {
                setLoading(false);
            }
        }

        fetchArticleAndUsers();
    }, [id]);

    useEffect(() => {
        async function getVotes() {
            if (!article) return;
    
            const endpoints = [
                { type: "Article", id: article.id },
                ...article.fact_checks.map(fc => ({ type: "FactCheck", id: fc.id })),
                ...article.comments.map(c => ({ type: "Comment", id: c.id })),
            ];
    
            const fetches = await Promise.all(
                endpoints.map(({ type, id }) =>
                    fetch(`/votes/${type}/${id}`)
                        .then(res => res.json())
                        .then(data => ({ [`${type}-${id}`]: data }))
                        .catch(() => ({ [`${type}-${id}`]: { likes: 0, dislikes: 0 } }))
                )
            );
    
            const mergedVotes = Object.assign({}, ...fetches);
            setVotesMap(mergedVotes);
        }
    
        getVotes();
    }, [article]);

    async function updateVotes(type, id, voteType) {
        try {
            if (!user.id) {
                console.error('No user logged in');
                return;
            }
    
            let voteValue;
        
            if (voteType.toLowerCase() === 'like') {
                voteValue = 1;
            } else if (voteType.toLowerCase() === 'dislike') {
                voteValue = -1;
            } else {
                console.error("Error: vote type invalid");
                return;
            }
        
            const key = `${type}-${id}`;
            const previousVote = votesMap[key]?.value || 0; 
        
            if (previousVote === voteValue) {
                voteValue = 0; // Clicking again cancels the vote
            }
        
            const response = await fetch(`/votes/${type}/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: user.id, value: voteValue }),
            });
            
            if (!response.ok) {
                console.error('Failed to update vote');
                return;
            }
        
            const updatedVotes = await response.json();
        
            setVotesMap(prevVotes => ({
                ...prevVotes,
                [key]: {
                    value: voteValue, 
                    likes: updatedVotes.likes,
                    dislikes: updatedVotes.dislikes
                }
            }));
        } catch (error) {
            console.error('Error updating vote:', error);
        }
    }
    
    
    

    if (loading) {
        return(
            <div className="loading-wrapper">
                <div className="spinner"></div>
            </div>
        )
    }

    if (!article) {
        return <div>No article found.</div>;
    }

    return (
        <div className="individual-article">
            <a href={article.url} className="individual-article-link">
                <div className="article-container">
                    <h1 className="article-title">{article.title}</h1>
                    <img
                        className="article-image"
                        src={article.image_url}
                        alt={article.title}
                    />
                    <div className="article-info">
                        <h3>{article.fact_checks[0]?.fact_check_level_label}</h3>
                        <h3>Posted: {formatDate(article.created_at)}</h3>
                    </div>
                </div>
            </a>
            <div className="article-likes">
                <button className="button-class" onClick={() => updateVotes('Article', article.id, 'like')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-160v-487L216-423l-56-57 320-320 320 320-56 57-224-224v487h-80Z"/></svg>{votesMap[`Article-${article.id}`]?.likes || 0}</button>
                <button className="button-class" onClick={() => updateVotes('Article', article.id, 'dislike')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-800v487L216-537l-56 57 320 320 320-320-56-57-224 224v-487h-80Z"/></svg>{votesMap[`Article-${article.id}`]?.dislikes || 0}</button>
            </div>
            <div className="fact-checks">
                {article.fact_checks.length > 0 ? (
                    article.fact_checks.map((fact_check, index) => (
                        <div className="individual-fact-check" key={index}>
                            <h3>{fact_check.fact_check_level_label}</h3>
                            {fact_check.content && <h3>{fact_check.content}</h3>}
                            {fact_check.fact_check_url && (
                                <a href={fact_check.fact_check_url} target="_blank" rel="noopener noreferrer">
                                    source
                                </a>
                            )}
                            <div>
                                <button className="button-class" onClick={() => updateVotes('FactCheck', fact_check.id, 'like')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-160v-487L216-423l-56-57 320-320 320 320-56 57-224-224v487h-80Z"/></svg>{votesMap[`FactCheck-${fact_check.id}`]?.likes || 0}</button>
                                <button className="button-class" onClick={() => updateVotes('FactCheck', fact_check.id, 'dislike')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-800v487L216-537l-56 57 320 320 320-320-56-57-224 224v-487h-80Z"/></svg>{votesMap[`FactCheck-${fact_check.id}`]?.dislikes || 0}</button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="individual-fact-check">
                        <h3>No fact checks yet</h3>
                    </div>
                )}
            </div>

            <div className="comment-container">
                <h1>Comments</h1>
                {article.comments.length > 0 ? (
                    article.comments.map((comment, index) => (
                        <div className="individual-comment" key={index}>
                            <div className="comment-main">
                                <h2 className="comment-user">
                                    {userMap[comment.user_id]?.username || "deleted"}
                                </h2>
                                <p className="comment-content">{comment.content}</p>
                            </div>
                            <p className="comment-meta">
                                {comment.updated_at !== comment.created_at ? (
                                    <span>Updated: {formatDate(comment.updated_at)}</span>
                                ) : (
                                    <span>Posted: {formatDate(comment.created_at)}</span>
                                )}
                            </p>
                            <div>
                                <button className="button-class" onClick={() => updateVotes('Comment', comment.id, 'like')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-160v-487L216-423l-56-57 320-320 320 320-56 57-224-224v487h-80Z"/></svg>{votesMap[`Comment-${comment.id}`]?.likes || 0}</button>
                                <button className="button-class" onClick={() => updateVotes('Comment', comment.id, 'dislike')}><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-800v487L216-537l-56 57 320 320 320-320-56-57-224 224v-487h-80Z"/></svg>{votesMap[`Comment-${comment.id}`]?.dislikes || 0}</button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="individual-comment">
                        <h3>No comments yet</h3>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ArticlePage;
