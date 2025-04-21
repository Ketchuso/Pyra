import { useLocation } from "react-router-dom";

function Home() {
    const { search } = useLocation();
    const params = new URLSearchParams(search);

    const filter = params.get("filter") || "news";
    const sort = params.get("sort") || "hot";

    return (
        <>
            <div class="main-page-contents">
            <h2>{`${filter[0].toUpperCase() + filter.slice(1)} Posts - ${sort[0].toUpperCase() + sort.slice(1)}`}</h2>
            </div>
        </>
    )
}

export default Home