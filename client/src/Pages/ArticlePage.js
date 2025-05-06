import React, { useEffect, useState } from "react";
import { useNavigate, useOutletContext, useParams } from "react-router-dom";

function ArticlePage() {
    const { user } = useOutletContext();
    const { id } = useParams();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [userMap, setUserMap] = useState({});
    const [newVote, setNewVote] = useState(true);
    const [votesMap, setVotesMap] = useState({});
    const [votableType, setVotableType] = useState("Article");
    const [editArticle, setEditArticle] = useState(false);
    const [newTitle, setNewTitle] = useState('')
    const [newImageUrl, setNewImageUrl] = useState('')
    const [newArticleUrl, setNewArticleUrl] = useState('')
    const [deleteArticle, setDeleteArticle] = useState(false)
    const navigate = useNavigate();
    const [addComment, setAddComment] = useState(false)
    const [content, setContent] = useState('')
    const [addFactCheck, setAddFactCheck] = useState(false);
    const [factCheckContent, setFactCheckContent] = useState('');
    const [factCheckLevel, setFactCheckLevel] = useState('')
    const [fact_check_url, setFactCheckUrl] = useState('')


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
    
    function onEditClick() {
        setEditArticle(!editArticle);
    }

    function onDeleteArticle(){
        setDeleteArticle(!deleteArticle);
    }

    function onAddComment(){
        setAddComment(!addComment);
    }

    function onFactCheck(){
        setAddFactCheck(!addFactCheck);
        setFactCheckContent('');
        setFactCheckLevel('');
        setFactCheckUrl('');
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

    function updateArticle(e) {
        e.preventDefault();
    
        const updatedFields = {};
        if (newTitle?.trim()) updatedFields.title = newTitle.trim();
        if (newImageUrl?.trim()) updatedFields.image_url = newImageUrl.trim();
        if (newArticleUrl?.trim()) updatedFields.url = newArticleUrl.trim();
    
        if (Object.keys(updatedFields).length === 0) {
            alert("No changes to update.");
            return;
        }
    
        fetch(`/article/${id}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(updatedFields),
        })
        .then(r => {
            if (r.ok) {
                return r.json().then(data => {
                    alert("Successfully updated article!");
                    console.log("Updated Info:", data);
                });
            } else {
                return r.json().then(error => {
                    alert("Something went wrong");
                    console.log("Server error:", error);
                });
            }
        })
        .catch(err => {
            alert("Sorry something went wrong on our end");
            console.error("Error updating post:", err);
        });
    }    

    function removeArticle() {
        fetch(`/article/${id}`, {
            method: "DELETE",
        })
        .then(async r => {
            if (r.ok) {
                // Only parse JSON if there's a response body (204 means no content)
                if (r.status !== 204) {
                    const data = await r.json();
                    console.log("Deleted Info:", data);
                }
                navigate("/?sort=hot")
                alert("Successfully deleted article!");
            } else {
                const error = await r.json();
                alert("Something went wrong");
                console.log("Server error:", error);
            }
        })
        .catch(err => {
            alert("Sorry something went wrong on our end");
            console.error("Error deleting post:", err);
        });
    }

    function submitComment(e) {
        e.preventDefault()
        let body = {};
    
        if (!content) {
            alert("There has to be content to comment");
            return;
        }
    
        body.content = content;
    
        if (!user.id) {
            alert("Error, user has no id");
            return;
        }
    
        body.user_id = user.id;
    
        if (!id) {
            alert("Error Article id doesn't exist");
            return;
        }
    
        body.article_id = parseInt(id);
    
        fetch('/create_comment', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        })
        .then(async r => {
            const data = await r.json();
            if (r.ok) {
                alert("Successfully posted a new comment!");
                console.log("Created comment:", data);
                setContent('');
                onAddComment();
            } else {
                alert("Sorry something went wrong");
                console.log("Server error:", data);
                setContent('');
                onAddComment();
            }
        })
        .catch(err => {
            alert("Sorry something went wrong on our end!");
            console.error("Error creating comment:", err);
            onAddComment();
        });        
    }
    
    function submitFactCheck(e) {
        e.preventDefault()
        let body = {};
    
        if (!factCheckContent) {
            alert("There has to be content to fact check");
            return;
        }
    
        body.content = factCheckContent;
    
        if (!user.id) {
            alert("Error, user has no id");
            return;
        }
    
        body.user_id = user.id;
    
        if (!id) {
            alert("Error Article id doesn't exist");
            return;
        }
    
        body.article_id = parseInt(id);

        if (!factCheckLevel){
            alert("Has to have fact check level");
            return;
        }

        const parsedLevel = parseInt(factCheckLevel);
        if (isNaN(parsedLevel) || parsedLevel < 0 || parsedLevel > 4) {
            alert("Invalid fact check level: must be a number between 0 and 4");
            return;
        }        
        
        body.fact_check_level = parsedLevel;

        if (fact_check_url) {
            body.fact_check_url = fact_check_url;
        }
    
        fetch('/create_fact_check', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        }).then(r => {
            if (r.ok) {
                return r.json().then(data => {
                    alert("Successfully posted a new fact check!");
                    console.log("Created fact check:", data);
                    onFactCheck();
                });
            } else {
                return r.json().then(error => {
                    alert("Sorry something went wrong");
                    console.log("Server error:", error);
                    onFactCheck();
                });
            }
        })        
        .catch(err =>{
            alert("Sorry something went wrong on our end!")
            console.error("Error creating fact check:", err)
            onFactCheck();
        })
        
    }

    return (
        <div className="individual-article">
            
                {editArticle && (
                    <div className="form-container">
                        <button onClick={() => onEditClick()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg></button>
                        <form onSubmit={e => updateArticle(e)}>
                            <label>
                                Title:
                                <input
                                type="text"
                                name="title"
                                placeholder="title..."
                                onChange={e => setNewTitle(e.target.value)}
                                />
                            </label>
                            <br />
                            <label>
                                Image Url:
                                <input 
                                type="text" 
                                name="image_url" 
                                placeholder="image url..." 
                                onChange={(e) => setNewImageUrl(e.target.value)}
                                />
                            </label>
                            <br />
                            <label>
                                Article Url:
                                <input 
                                type="text" 
                                name="article_url" 
                                placeholder="article url..." 
                                onChange={(e) => setNewArticleUrl(e.target.value)}
                                />
                            </label>
                            <br />
                            <button className="button-class" type="submit">Submit</button>
                            <h4>You don't have to update every field</h4>
                            <h4>Refresh page to see changes</h4>
                        </form>
                    </div>
                )}
                {deleteArticle && (
                    <div className="form-container">
                        <h1>Are you Sure you would like to this?</h1>
                        <h3>You can't undo a deleted article</h3>
                        <div>
                            <button onClick={() => removeArticle()} className="button-class">finish them</button>
                            <button onClick={() => onDeleteArticle()} className="button-class">go back</button>
                        </div>
                    </div>
                )}
                {addComment && (
                    <div className="form-container">
                        <button onClick={() => onAddComment()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg></button>
                        <form onSubmit={e => submitComment(e)}>
                            <label>
                                Comment:
                                <input
                                type="text"
                                name="content"
                                placeholder="content..."
                                onChange={e => setContent(e.target.value)}
                                />
                            </label>
                            <br />
                            <button className="button-class" type="submit">Submit</button>
                            <h4>Refresh page to see changes</h4>
                        </form>
                    </div>
                )}
                {addFactCheck && (
                    <div className="form-container">
                        <button onClick={() => onFactCheck()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg></button>
                        <form onSubmit={e => submitFactCheck(e)}>
                            <label>
                                Content:
                                <input
                                type="text"
                                name="fact check content"
                                placeholder="content..."
                                onChange={e => setFactCheckContent(e.target.value)}
                                />
                            </label>
                            <br />
                            <label>
                                Fact Check Level:
                                <input
                                type="text"
                                name="fact check level"
                                placeholder="0-4, (0 = Unverified, 4 = verified)"
                                onChange={e => setFactCheckLevel(e.target.value)}
                                />
                            </label>
                            <br />
                            <label>
                                Fact Check Url (optional):
                                <input
                                type="text"
                                name="fact check url"
                                placeholder="something to back up your fact check"
                                onChange={e => setFactCheckUrl(e.target.value)}
                                />
                            </label>
                            <br />
                            <button className="button-class" type="submit">Submit</button>
                            <h4>Refresh page to see changes</h4>
                        </form>
                    </div>
                )}
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
                {user && (<button onClick={()=> onFactCheck()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/></svg></button>)}
                {user && user.id === article.submitted_by_id && (
                    <>
                        <button onClick={() => onEditClick()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/></svg></button>
                        <button onClick={() => onDeleteArticle()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/></svg></button>
                    </>
                )}
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
            {user && (<button onClick={()=> onAddComment()} className="button-class"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/></svg></button>)}
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
