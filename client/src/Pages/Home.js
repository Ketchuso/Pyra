import { useState, useEffect } from "react";

function Home() {
    const [articles, setArticles] = useState([]); // Default to empty array
    const [loading, setLoading] = useState(true); // Track loading state

    useEffect(() => {
        fetch("/articles", {
            method: "GET"
        })
        .then(resp => resp.json())
        .then(data => {
            // Now directly check if data is an array
            if (Array.isArray(data)) {
                setArticles(data);  // Set articles directly to the data received
                console.log("Fetched Articles:", data);  // Log the fetched articles
            } else {
                console.error("Error: Data is not in expected format", data);
            }
            setLoading(false); // Set loading to false after data is fetched
        })
        .catch(error => {
            console.error("Error fetching articles:", error);
            setLoading(false); // Set loading to false even if there's an error
        });
    }, []); // Runs only once, on mount

    return (
        <>
            <div className="main-page-contents">
                {/* Show loading text or spinner while fetching data */}
                {loading ? (
                    <div>Loading...</div> // You can also replace this with a spinner component
                ) : (
                    <ul>
                        {articles.length > 0 ? (
                            articles.map((article) => (
                                // Use a unique identifier (e.g., article.id or article.url) as the key
                                <div className="article-container" key={article.id || article.url}>
                                    {/* Preview Image */}
                                    <h3>{article.title}</h3>
                                    <img className="article-image" src={article.imageUrl} alt={article.title} /> {/* Add an image URL here */}
                                    {/* Bottom-aligned info */}
                                    <div className="article-info">
                                        <h3>Fact Checked:</h3>
                                        <h3>Posted at: {article.created_at}</h3>
                                        <h3>
                                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                                                Link
                                            </a>
                                        </h3> 
                                    </div>
                                </div>
                            ))
                        ) : (
                            <li>No articles available.</li>
                        )}
                    </ul>
                )}
            </div>
        </>
    );
}

export default Home;
