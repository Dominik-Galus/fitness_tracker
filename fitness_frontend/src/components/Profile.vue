<template>
  <div class="site-container profile-container">
    <h2 class="page-title">Profile</h2>
    <div v-if="loading" class="loading-spinner">
      <span class="loader"></span>
    </div>
    <div v-else>
      <form @submit.prevent="updateProfile" class="form-group profile-form">
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
        <button @click="confirmDelete" class="submit-btn delete-btn">
          <span class="btn-icon">🗑️</span> Delete Account
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
    async confirmDelete() {
      if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
        await this.deleteAccount();
      }
    },
    async deleteAccount() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const password = prompt("Please enter your password to confirm account deletion:");
        if (!password) {
          return;
        }

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.post(`${apiUrl}/auth/delete`, {
          access_token: token,
          password: password,
        });

        localStorage.removeItem("access_token");
        this.$router.push("/login");
      } catch (error) {
        this.error = "Failed to delete account. Please try again.";
      }
    },
  },
};
</script>

<style scoped>
.profile-container {
  max-width: 500px;
}

.profile-form {
  gap: 20px;
}

.submit-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

.delete-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border-radius: 5px;
  font-size: 16px;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.delete-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

.success-message {
  font-size: 16px;
  color: #27ae60;
  text-align: center;
  margin-top: 20px;
}

</style>
