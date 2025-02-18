<template>
  <div class="dashboard-container">
    <h2 class="page-title">Dashboard</h2>
    <div class="welcome-message">
      <p>Welcome, <span class="username">{{ username }}</span>!</p>
    </div>
    <div class="quick-links">
      <router-link to="/trainings" class="quick-link">
        <span class="link-icon">🏋️</span> My Trainings
      </router-link>
      <router-link to="/profile" class="quick-link">
        <span class="link-icon">👤</span> My Profile
      </router-link>
    </div>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";
import axios from "../axios.js";

export default {
  data() {
    return {
      username: '',
    };
  },
  created() {
    this.checkAuthentication();
  },
  methods: {
    checkAuthentication() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push('/login');
      } else {
        try {
          const decoded = jwtDecode(token);
          this.username = decoded.sub;
        } catch (error) {
          console.error("Invalid token", error);
          this.$router.push('/login');
        }
      }
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  max-width: 800px;
  margin: 50px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
}

.welcome-message {
  font-size: 20px;
  color: #34495e;
  margin-bottom: 30px;
}

.welcome-message .username {
  font-weight: 600;
  color: #3498db;
}

.quick-links {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.quick-link {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px 20px;
  color: #fff;
  background-color: #2c3e50;
  border-radius: 8px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.quick-link:hover {
  transform: translateY(-2px);
  background-color: #34495e;
}

.quick-link .link-icon {
  margin-right: 8px;
  font-size: 18px;
}
</style>
