<template>
  <div class="profile-container">
    <h2>Profile</h2>
    <div v-if="loading">Loading profile...</div>
    <div v-else>
      <form @submit.prevent="updateProfile" class="profile-form">
        <div class="form-group">
          <label for="age">Age:</label>
          <input type="number" v-model="profile.age" id="age" required />
        </div>
        <div class="form-group">
          <label for="height">Height (cm):</label>
          <input type="number" v-model="profile.height" id="height" required />
        </div>
        <div class="form-group">
          <label for="weight">Weight (kg):</label>
          <input type="number" v-model="profile.weight" id="weight" required />
        </div>
        <button type="submit" class="submit-btn">Update Profile</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import { jwtDecode } from "jwt-decode";
import { useRouter } from "vue-router";

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
        const router = useRouter();
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.push("/login");
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
        const router = useRouter();
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.push("/login");
          return;
        }

        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.put(`${apiUrl}/profile/update/${user_id}`, this.profile);

        this.success = "Profile updated successfully!";
        this.error = "";
      } catch (error) {
        this.error = "Failed to update profile. Please try again.";
        this.success = "";
      }
    },
  },
};
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  align-items: center;
}

.form-group {
  display: contents;
}

label {
  font-weight: 600;
  text-align: right;
  padding-right: 10px;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 100%;
}

.submit-btn {
  grid-column: span 2;
  padding: 10px;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.submit-btn:hover {
  background-color: #34495e;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}

.success {
  color: green;
  margin-top: 10px;
  text-align: center;
}
</style>
