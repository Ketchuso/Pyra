import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function ArticlePage() {
    const { id } = useParams();
    console.log("Article ID from route:", id);

    const [article, setArticle] = useState(null); // Initialize with null since it's a single article
    const [loading, setLoading] = useState(true);

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
        fetch(`/article/${id}`, {
            method: "GET"
        })
            .then(resp => resp.json())
            .then(data => {
                if (data) {
                    setArticle(data); // Set article directly as an object
                    console.log("Fetched Article:", data);
                } else {
                    console.error("Error: Data is not in expected format", data);
                }
                setLoading(false); // Stop loading when the data is fetched
            })
            .catch(error => {
                console.error("Error fetching article:", error);
                setLoading(false); // Stop loading in case of an error
            });
    }, [id]); // Re-fetch if `id` changes

    if (loading) {
        return <div>Loading...</div>; // Show loading message while fetching data
    }

    // If article is available, render its details
    if (article) {
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
                <div className="fact-checks">
                    {article.fact_checks.length > 0 ? (
                        article.fact_checks.map((fact_check, index) => (
                        <div class="individual-fact-check" key={index}>
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
                        <div>
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
                              <h2 className="comment-user">User ID: {comment.user_id}</h2>
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
                        <div>
                            <h3>No comments yet</h3>
                        </div>
                    )}
                </div>

            </div>
            
        );
    }
    

    return <div>No article found.</div>; // Fallback if no article is found
}

export default ArticlePage;
