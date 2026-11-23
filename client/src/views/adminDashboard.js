import csrfFetch from '../csrfFetch';
import { useState } from 'react';
import CreateCustomerRep from './createCustRep';
import SalesReport from './salesReport';
import ResetRequests from './resetRequests';
import '../styles/adminDashboard.css';

export default function AdminDashboard() {
  const [activeSection, setActiveSection] = useState('create');

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

  const renderPanel = () => {
    switch (activeSection) {
      case 'sales':
        return <SalesReport />;
      case 'reset':
        return <ResetRequests />;
      case 'create':
      default:
        return <CreateCustomerRep />;
    }
  };

  return (
    <div className="admin-dashboard-container">
      <header className="admin-header">
        <div className="admin-header-title">
          <span className="ikea-logo">JustBIDit</span>
          <span className="dashboard-title">Admin Dashboard</span>
        </div>
        <button onClick={handleLogout} className="ikea-logout-btn">Logout</button>
      </header>

      <div className="admin-body">
        <aside className="admin-sidebar">
          <ul>
            <li onClick={() => setActiveSection('create')}>Create Customer Rep</li>
            <li onClick={() => setActiveSection('sales')}>Sales Report</li>
            <li onClick={() => setActiveSection('reset')}>Reset Requests</li>
          </ul>
        </aside>

        <main className="admin-main">
          {renderPanel()}
        </main>
      </div>
    </div>
  );
}
