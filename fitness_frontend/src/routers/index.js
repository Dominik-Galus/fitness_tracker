import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/Login.vue";
import Dashboard from "../components/Dashboard.vue";
import Register from "../components/Register.vue";
import Profile from "../components/Profile.vue";
import Trainings from "../components/Trainings.vue";
import TrainingDetails from "../components/TrainingDetails.vue";
import CreateTraining from "../components/CreateTraining.vue";

const routes = [
    {
        path: "/login",
        component: Login,
    },
    {
        path: "/",
        component: Dashboard,
        meta: { requiresAuth: true },
    },
    {
        path: "/register",
        component: Register,
    },
    {
        path: "/profile",
        component: Profile,
    },
    {
        path: "/trainings",
        component: Trainings,
    },
    {
        path: "/trainings/:id",
        component: TrainingDetails,
        props: true,
    },
    {
        path: "/trainings/create",
        component: CreateTraining,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
