import React from 'react';

export default function ActiveUsers({ users }) {
    if (!users || users.length === 0) return null;

    return (
        <div className="section-block" style={{ marginTop: '20px' }}>
            <h3>🏆 En Aktif Kullanıcılar</h3>
            <table className="admin-table">
                <thead>
                    <tr>
                        <th>Kullanıcı</th>
                        <th>Yorum Sayısı</th>
                        <th>Beğeni Sayısı</th>
                        <th>Toplam Puan</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map((user, index) => (
                        <tr key={user.id}>
                            <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    {/* Rank Badge */}
                                    <span style={{
                                        display: 'inline-flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        width: '24px',
                                        height: '24px',
                                        borderRadius: '50%',
                                        backgroundColor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#333',
                                        color: index < 3 ? '#000' : '#fff',
                                        fontWeight: 'bold',
                                        fontSize: '0.8em'
                                    }}>
                                        {index + 1}
                                    </span>
                                    <div>
                                        <div style={{ fontWeight: 'bold' }}>{user.username}</div>
                                        <div style={{ fontSize: '0.8em', color: '#888' }}>{user.email}</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <span style={{ color: '#00e5ff' }}>{user.review_count}</span>
                            </td>
                            <td>
                                <span style={{ color: '#ff4081' }}>{user.like_count}</span>
                            </td>
                            <td>
                                <span style={{ fontWeight: 'bold', fontSize: '1.1em', color: '#4caf50' }}>
                                    {user.total_score}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
