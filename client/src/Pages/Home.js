import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

function Home() {
    const [articles, setArticles] = useState([]);
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
        fetch("/articles", {
            method: "GET"
        })
        .then(resp => resp.json())
        .then(data => {
            if (Array.isArray(data)) {
                setArticles(data);
                console.log("Fetched Articles:", data);
            } else {
                console.error("Error: Data is not in expected format", data);
            }
            setLoading(false);
        })
        .catch(error => {
            console.error("Error fetching articles:", error);
            setLoading(false);
        });
    }, []);

    return (
        <div className="main-page-contents">
            {loading ? (
                <div>Loading...</div>
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
                                        <h3>{article.fact_checks[0]?.fact_check_level_label}</h3>
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
