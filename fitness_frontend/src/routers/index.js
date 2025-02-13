import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/Login.vue";
import Dashboard from "../components/Dashboard.vue";
import Register from "../components/Register.vue";

const routes = [
    {
        path: "/login",
        component: Login,
    },
    {
        path: "/dashboard",
        component: Dashboard,
        meta: { requiresAuth: true },
    },
    {
        path: "/register",
        component: Register,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
