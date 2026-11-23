import csrfFetch from '../csrfFetch';
import { useState } from 'react';
import Questions from './custQuestions';
import ManageAuctions from './custManageAuctions';
import ManageBids from './custManageBids';
import ManageUsers from './custManageUsers';
import '../styles/custRepDashboard.css';


export default function CustomerRepDashboard() {
  const [activeView, setActiveView] = useState('questions');

  const handleLogout = async () => {
  try {
    const response = await csrfFetch('/admin/logout', {
      method: 'POST',
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Logout failed');
    }

    window.location.href = '/admin-login';
  } catch (error) {
    console.error('Logout error:', error);
    alert('Unable to log out. Please try again.');
  }
};

  const renderView = () => {
    switch (activeView) {
      case 'questions':
        return <Questions />;
      case 'users': return <ManageUsers />;
      case 'bids': return <ManageBids />;
      case 'auctions': return <ManageAuctions />;
      default:
        return <div>Select a section from the sidebar</div>;
    }
  };

  return (
    <div className="rep-dashboard-container">
      <header className="rep-header">
        <div className="rep-header-title">
          <span className="ikea-logo">JustBIDit</span>
          <span className="dashboard-title">Customer Rep Dashboard</span>
        </div>
        <button onClick={handleLogout} className="ikea-logout-btn">Logout</button>
      </header>

      <div className="rep-body">
        <aside className="rep-sidebar">
          <ul>
            <li onClick={() => setActiveView('questions')}>Questions</li>
            <li onClick={() => setActiveView('users')}>Manage Users</li>
            <li onClick={() => setActiveView('bids')}>Manage Bids</li>
            <li onClick={() => setActiveView('auctions')}>Manage Auctions</li>
          </ul>
        </aside>

        <main className="rep-main">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
