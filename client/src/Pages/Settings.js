import React, {useState} from "react";
import { useOutletContext, useParams } from "react-router-dom";

function Settings(){
    const { user } = useOutletContext();
    const [newUsername, setNewUsername] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [newEmailConfirmation, setNewEmailConfirmation] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [newPasswordConfirmation, setNewPasswordConfirmation] = useState('');
    const { id } = useParams();

    async function handleSubmit(e) {
        e.preventDefault();
    
        if (!newUsername && !newEmail && !newPassword) {
            alert("Please provide at least one field to update");
            return;
        }
    
        if (newEmail && newEmailConfirmation) {
            if (newEmail.trim() !== newEmailConfirmation.trim()) {
              alert("The email and email confirmation don't match");
              return;
            }
          }
      
    
        if (newPassword && newPasswordConfirmation) {
            if (newPassword.trim() !== newPasswordConfirmation.trim()) {
                alert("The password and password confirmation don't match");
                return;
            }
        }
    
        const body = {};
    
        if (newUsername !== '') {
            body.username = newUsername.trim();
        }
    
        if (newEmail !== '') {
            body.email = newEmail.trim();
        }
    
        if (newPassword !== '') {
            body.password = newPassword.trim();
        }
    
        try {
            const response = await fetch(`/user/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(body),
            });
    
            if (response.ok) {
                alert("Updated your info!");
            } else {
                const err = await response.json();
                alert(err.error || "Update failed.");
            }
        } catch (error) {
            console.error("Update error:", error);
            alert("An error occurred.");
        }
    }
    

    return (
        <>
          {user ? (
            <>
              <h1>Edit User</h1>
      
              <form className="form-container" onSubmit={e => handleSubmit(e)}>
                <label>
                  Update Username:
                  <input 
                    type="text" 
                    name="username" 
                    placeholder="username..." 
                    onChange={(e) => setNewUsername(e.target.value)}
                  />
                </label>
                <br />
      
                <label>
                  Update Email:
                  <input 
                    type="text" 
                    name="new_email" 
                    placeholder="new email..." 
                    onChange={(e) => setNewEmail(e.target.value)}
                  />
                </label>
                <br />
                {newEmail && (
                  <>
                    <label>
                      New Email Confirmation:
                      <input 
                        type="text" 
                        name="email_confirmation" 
                        placeholder="email confirmation..." 
                        onChange={(e) => setNewEmailConfirmation(e.target.value)} 
                      />
                    </label>
                    <br />
                  </>
                )}
      
                <label>
                  Update Password:
                  <input 
                    type="text" 
                    name="new_password" 
                    placeholder="new password..." 
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                </label>
                <br />

                {newPassword && (
                  <>
                    <label>
                      New Password Confirmation:
                      <input 
                        type="text" 
                        name="Password_Confirmation" 
                        placeholder="password confirmation..." 
                        onChange={(e) => setNewPasswordConfirmation(e.target.value)} 
                      />
                    </label>
                    <br />
                  </>
                )}
      
                <button className="button-class" type="submit">Submit</button>
              </form>
            </>
          ) : (
            <h1 className="center-text">Have to be logged in to change settings silly goose! 🪿</h1>
          )}
        </>
      );
      
}

export default Settings