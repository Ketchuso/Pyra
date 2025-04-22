import { useState, useEffect } from "react";

function Home() {
    const [articles, setArticles] = useState([]); // Default to empty array
    const [loading, setLoading] = useState(true); // Track loading state

    // Helper function to format the date
    const formatDate = (dateString) => {
        // Convert "YYYY-MM-DD HH:MM:SS" to ISO format
        if (dateString.includes(' ')) {
            dateString = dateString.replace(' ', 'T') + 'Z';
        }
    
        const articleDate = new Date(dateString);
        console.log("Converted date:", articleDate);
    
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
                                <div className="article-container" key={article.id || article.url}>
                                    {/* Preview Image */}
                                    <h3 className="article-title">{article.title}</h3>
                                    <img className="article-image" src={article.image_url} alt={article.title} /> 
                                    {/* Bottom-aligned info */}
                                    <div className="article-info">
                                        <h3>Fact Checked:</h3>
                                        <h3>Posted @{formatDate(article.created_at)}</h3>
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
