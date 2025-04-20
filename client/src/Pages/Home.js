import { useLocation } from "react-router-dom";

function Home() {
    const { search } = useLocation();
    const params = new URLSearchParams(search);

    const filter = params.get("filter") || "news";
    const sort = params.get("sort") || "hot";

    return (
        <>
            <h2>{`${filter[0].toUpperCase() + filter.slice(1)} Posts - ${sort[0].toUpperCase() + sort.slice(1)}`}</h2>
            <h1>Pyra</h1>
            <p>Home Page</p>
        </>
    )
}

export default Home