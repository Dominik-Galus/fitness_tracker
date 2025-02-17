<template>
  <div>
    <nav class="navbar">
      <ul>
        <li><router-link to="/">Home</router-link></li>
        <li v-if="isAuthenticated"><router-link to="/profile">Profile</router-link></li>
        <li v-if="isAuthenticated"><router-link to="/trainings">Trainings</router-link></li>

        <li v-if="!isAuthenticated"><router-link to="/login">Login</router-link></li>
        <li v-if="!isAuthenticated"><router-link to="/register">Register</router-link></li>

        <li v-if="isAuthenticated"><a href="#" @click="logout">Logout</a></li>
      </ul>
    </nav>

    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import eventBus from "./eventBus";
import "./assets/global.css"

export default {
  setup() {
    const router = useRouter();
    const isAuthenticated = ref(!!localStorage.getItem("access_token"));

    onMounted(() => {
      eventBus.on("auth-change", () => {
        isAuthenticated.value = !!localStorage.getItem("access_token");
      });
    });

    const logout = () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      eventBus.emit("auth-change");
      router.push("/login");
    };

    return {
      isAuthenticated,
      logout,
    };
  },
};
</script>

<style scoped>
.navbar {
  background-color: #2c3e50;
  padding: 15px;
  display: flex;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.navbar ul {
  list-style: none;
  display: flex;
  padding: 0;
  margin: 0;
  gap: 20px;
}

.navbar li {
  margin: 0;
}

.navbar a {
  text-decoration: none;
  color: #ecf0f1;
  font-weight: 600;
  font-size: 16px;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
}

.navbar a:hover {
  background-color: #34495e;
  transform: translateY(-2px);
}

.navbar a.router-link-exact-active {
  color: #fff;
  background-color: #34495e;
}

.content {
  padding: 20px;
  text-align: center;
}
</style>
