// Authentication utilities using localStorage

// Simple hash simulation (not cryptographically secure - for demo only)
const hashPassword = (password) => {
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16);
};

export const auth = {
  // Get current logged-in user
  getCurrentUser: () => {
    try {
      const user = localStorage.getItem('greenrewards_user');
      return user ? JSON.parse(user) : null;
    } catch (e) {
      console.error('Error parsing user from localStorage:', e);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return auth.getCurrentUser() !== null;
  },

  // Register new user
  register: (fullName, email, password, confirmPassword) => {
    // Validation
    if (!fullName || !email || !password || !confirmPassword) {
      return { success: false, error: 'All fields are required' };
    }
    if (password !== confirmPassword) {
      return { success: false, error: 'Passwords do not match' };
    }
    if (password.length < 6) {
      return { success: false, error: 'Password must be at least 6 characters' };
    }
    if (!email.includes('@')) {
      return { success: false, error: 'Invalid email format' };
    }

    // Check if user already exists
    const users = JSON.parse(localStorage.getItem('greenrewards_users') || '[]');
    if (users.some(u => u.email === email)) {
      return { success: false, error: 'User with this email already exists' };
    }

    // Create new user
    const newUser = {
      id: Date.now().toString(),
      name: fullName,
      email,
      password: hashPassword(password), // Simple hash - not for production
      ecoScore: 50,
      ecoPoints: 0,
      achievements: [],
      createdAt: new Date().toISOString()
    };

    // Store user in list and set as current
    users.push(newUser);
    localStorage.setItem('greenrewards_users', JSON.stringify(users));
    localStorage.setItem('greenrewards_user', JSON.stringify(newUser));

    return { success: true, user: newUser };
  },

  // Login user
  login: (email, password) => {
    if (!email || !password) {
      return { success: false, error: 'Email and password are required' };
    }

    const users = JSON.parse(localStorage.getItem('greenrewards_users') || '[]');
    const user = users.find(u => u.email === email && u.password === hashPassword(password));

    if (!user) {
      return { success: false, error: 'Invalid email or password' };
    }

    localStorage.setItem('greenrewards_user', JSON.stringify(user));
    return { success: true, user };
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('greenrewards_user');
  },

  // Update user profile
  updateUser: (updates) => {
    const user = auth.getCurrentUser();
    if (!user) return { success: false, error: 'Not authenticated' };

    const updatedUser = { ...user, ...updates };
    localStorage.setItem('greenrewards_user', JSON.stringify(updatedUser));

    // Also update in users list
    const users = JSON.parse(localStorage.getItem('greenrewards_users') || '[]');
    const index = users.findIndex(u => u.id === user.id);
    if (index !== -1) {
      users[index] = updatedUser;
      localStorage.setItem('greenrewards_users', JSON.stringify(users));
    }

    return { success: true, user: updatedUser };
  },

  // Update eco score and points after assessment
  updateAssessmentData: (ecoScore, ecoPoints, assessmentData) => {
    const user = auth.getCurrentUser();
    if (!user) return { success: false, error: 'Not authenticated' };

    const updatedUser = {
      ...user,
      ecoScore,
      ecoPoints: user.ecoPoints + ecoPoints,
      lastAssessment: {
        date: new Date().toISOString(),
        data: assessmentData,
        score: ecoScore,
        points: ecoPoints
      }
    };

    localStorage.setItem('greenrewards_user', JSON.stringify(updatedUser));

    // Also update in users list
    const users = JSON.parse(localStorage.getItem('greenrewards_users') || '[]');
    const index = users.findIndex(u => u.id === user.id);
    if (index !== -1) {
      users[index] = updatedUser;
      localStorage.setItem('greenrewards_users', JSON.stringify(users));
    }

    return { success: true, user: updatedUser };
  }
};
