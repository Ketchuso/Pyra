import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function ArticlePage() {
    const { id } = useParams();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [userMap, setUserMap] = useState({});
    const [newVote, setNewVote] = useState(true);
    const [votes, setVotes] = useState({ likes: 0, dislikes: 0 });
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
            // const votableType = "Article"; 
            const response = await fetch(`/votes/${votableType}/${id}`);
            const data = await response.json();
            setVotes(data);
        }

        getVotes();
    }, [id, article, newVote]);

    if (loading) {
        return <div>Loading...</div>;
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
                        <h3>{votes.likes} {votes.dislikes}</h3>
                        <h3>Posted: {formatDate(article.created_at)}</h3>
                    </div>
                </div>
            </a>

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
