# LeavePortal Database Name Updater Helper
# Run this script to update user names, usernames, and emails without losing leaves or tasks.

import sqlite3

def update_database_users():
    # 1. Connect to your active database file
    conn = sqlite3.connect('leave_system.db')
    cursor = conn.cursor()

    # 2. EDIT THESE VALUES TO YOUR LIKING:
    # Format: (New Display Name, New Username/Nickname, New Email, Old Username)
    user_updates = [
        # Example: Change Alice Smith
        ("Alice Smith", "alice", "alice@company.com", "alice"),
        
        # Example: Change Bob Jones
        ("Bob Jones", "bob", "bob@company.com", "bob"),
        
        # Example: Change Charlie Dev to Diyaana Dev (nickname: diyaana)
        ("Diyaana Dev", "diyaana", "diyaana@company.com", "charlie"),
        
        # Example: Change David Quality
        ("David Quality", "david", "david@company.com", "david"),
        
        # Example: Change Eve Design
        ("Eve Design", "eve", "eve@company.com", "eve"),
    ]

    print("\n--- Updating database records ---")
    updated_count = 0
    for name, username, email, old_username in user_updates:
        # Check if the old username exists in the database
        cursor.execute("SELECT id FROM users WHERE username = ?", [old_username])
        user = cursor.fetchone()
        
        if user:
            cursor.execute(
                "UPDATE users SET name = ?, username = ?, email = ? WHERE id = ?",
                (name, username, email, user[0])
            )
            print(f"Updated User ID {user[0]}: Name -> '{name}' | Username -> '{username}' | Email -> '{email}'")
            updated_count += 1
        else:
            # Check if it was already updated
            cursor.execute("SELECT id FROM users WHERE username = ?", [username])
            already_updated = cursor.fetchone()
            if already_updated:
                print(f"Skipping '{username}': Already updated previously (User ID {already_updated[0]}).")
            else:
                print(f"Warning: Old username '{old_username}' not found in database.")

    conn.commit()
    conn.close()
    
    if updated_count > 0:
        print("\nSuccess: Database updated successfully! All leaves and tasks are preserved.")
        print("Note: If you are currently logged in, please Log Out and Log In again in your browser to see the changes.")
    else:
        print("\nNo database updates were made. Check your old username strings in the script.")

if __name__ == '__main__':
    update_database_users()
