import React, {useState} from "react";
import { useOutletContext } from "react-router-dom";

function Settings(){
    const { user } = useOutletContext();
    const [newUsername, setNewUsername] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [newEmailConfirmation, setNewEmailConfirmation] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [newPasswordConfirmation, setNewPasswordConfirmation] = useState('');

    function handleSubmit(e){
        e.preventDefault();
        alert("submit handled")
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
      
                {newEmail !== '' && (
                  <>
                    <label>
                      New Email Confirmation:
                      <input 
                        type="text" 
                        name="email confirmation" 
                        placeholder="email confirmation..." 
                        onChange={(e) => setNewEmail(e.target.value)}
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

                {newPassword !== '' && (
                  <>
                    <label>
                      New Password Confirmation:
                      <input 
                        type="text" 
                        name="Password Confirmation" 
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