import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

function Home() {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const location = useLocation();

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

    const currentSort = new URLSearchParams(location.search).get('sort') || 'hot';
    useEffect(() => {
        const fetchArticles = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/articles?sort=${currentSort}`, {
                    method: "GET"
                });
                const data = await response.json();
    
                if (Array.isArray(data)) {
                    setArticles(data);
                } else {
                    console.error("Error: Data is not in expected format", data);
                    setArticles([]);
                }
            } catch (error) {
                console.error("Error fetching articles:", error);
                setArticles([]);
            } finally {
                setLoading(false);
            }
        };
    
        fetchArticles();
    }, [currentSort]);
    

    return (
        <div className="main-page-contents">
            {loading ? (
                <div className="loading-wrapper">
                    <div className="spinner"></div>
                </div>
            ) : (
                <ul>
                    {articles.length > 0 ? (
                        articles.map((article) => (
                            <Link
                                to={`/article/${article.id}`}
                                key={article.id || article.url}
                                className="article-link"
                                style={{ textDecoration: 'none', color: 'inherit' }}
                            >
                                <div className="article-container">
                                    <h3 className="article-title">{article.title}</h3>
                                    <img
                                        className="article-image"
                                        src={article.image_url}
                                        alt={article.title}
                                    />
                                    <div className="article-info">
                                    <h3>
                                        {
                                            article.fact_checks?.length > 0
                                            ? article.fact_checks
                                                .slice() 
                                                .sort((a, b) => b.hotness - a.hotness)[0].fact_check_level_label
                                            : "Unverified"
                                        }
                                        </h3>
                                        <h3>Posted: {formatDate(article.created_at)}</h3>
                                    </div>
                                </div>
                            </Link>
                        ))
                    ) : (
                        <li>No articles available.</li>
                    )}
                </ul>
            )}
        </div>
    );
}

export default Home;
