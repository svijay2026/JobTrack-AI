import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('user')); } catch { return null; }
  });
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    const res = await authService.login({ email, password });
    const token = res.data.access_token;
    localStorage.setItem('access_token', token);
    const me = await authService.me();
    localStorage.setItem('user', JSON.stringify(me.data));
    setUser(me.data);
    return me.data;
  };

  const register = async (email, password, fullName) => {
    await authService.register({ email, password, full_name: fullName });
    return login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
