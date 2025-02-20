<template>
  <div class="profile-container">
    <h2 class="page-title">Profile</h2>
    <div v-if="loading" class="loading-spinner">
      <span class="loader"></span>
    </div>
    <div v-else>
      <form @submit.prevent="updateProfile" class="profile-form">
        <div class="form-group">
          <label for="age">Age:</label>
          <input type="number" v-model="profile.age" id="age" required class="form-input" />
        </div>
        <div class="form-group">
          <label for="height">Height (cm):</label>
          <input type="number" v-model="profile.height" id="height" required class="form-input" />
        </div>
        <div class="form-group">
          <label for="weight">Weight (kg):</label>
          <input type="number" v-model="profile.weight" id="weight" required class="form-input" />
        </div>
        <button type="submit" class="submit-btn">
          <span class="btn-icon">💾</span> Update Profile
        </button>
      </form>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success-message">{{ success }}</p>
    </div>
  </div>
</template>

<script>
import axios from "../axios.js";
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      profile: {
        user_id: null,
        age: null,
        height: null,
        weight: null,
      },
      loading: true,
      error: "",
      success: "",
    };
  },
  created() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        const response = await axios.get(`${apiUrl}/profile/${user_id}`);

        this.profile = response.data;
        this.loading = false;
      } catch (error) {
        this.error = error;
        this.loading = false;
      }
    },
    async updateProfile() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.put(`${apiUrl}/profile/update/${user_id}`, this.profile);

        this.success = "Profile updated successfully!";
        this.error = "";
      } catch (error) {
        if (error.response.status == 422) {
            this.error = "Profile data must contain numbers greater than zero.";
        } else {
          this.error = "Failed to update profile. Please try again.";
        }
        this.success = "";
      }
    },
  },
};
</script>

<style scoped>
.profile-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.submit-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

.error-message {
  font-size: 16px;
  color: #e74c3c;
  text-align: center;
  margin-top: 20px;
}

.success-message {
  font-size: 16px;
  color: #27ae60;
  text-align: center;
  margin-top: 20px;
}
</style>
