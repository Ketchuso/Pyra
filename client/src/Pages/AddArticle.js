import React, { useState } from "react";
import { useOutletContext, useNavigate } from "react-router-dom";

function AddArticle(){
    const { user } = useOutletContext();
    const [newTitle, setNewTitle] = useState('')
    const [newImageUrl, setNewImageUrl] = useState('')
    const [newArticleUrl, setNewArticleUrl] = useState('')
    const navigate = useNavigate();

    function handleSubmit(e){
        e.preventDefault();
        fetch('/create_article', {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
            },
            body: JSON.stringify({
                title: newTitle,
                image_url: newImageUrl,
                url: newArticleUrl,
                submitted_by_id: user.id
            }),
        })
        .then(r => {
            if (r.ok) {
                return r.json().then(data => {
                    alert("Successfully posted a new article!");
                    console.log("Created article:", data);
                    navigate("/?sort=new")
                });
            } else {
                return r.json().then(error => {
                    alert("Sorry something went wrong");
                    console.log("Server error:", error);
                });
            }
        })        
        .catch(err =>{
            alert("Sorry something went wrong on our end!")
            console.error("Error creating post:", err)
        })
    }

    return (
        <>
          {user ? (
            <>
              <h1>Add Article</h1>
      
              <form className="form-container" onSubmit={e => handleSubmit(e)}>
                <label>
                  Title:
                  <input 
                  type="text" 
                  name="title" 
                  placeholder="title..." 
                  onChange={(e) => setNewTitle(e.target.value)}
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
              </form>
            </>
          ) : (
            <h1>Please login to post</h1>
          )}
        </>
    );
      
}

export default AddArticle;