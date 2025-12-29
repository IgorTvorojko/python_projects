import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import { api } from './api';

// Import views
import Host from './views/Host.vue';
import Game from './views/Game.vue';
import Profile from './views/Profile.vue';
import Home from './views/Home.vue';

// Define routes
const routes = [
    { path: '/', component: Home },
    { path: '/host', component: Host },
    { path: '/game/:id', component: Game, props: true },
    { path: '/profile', component: Profile },
];

// Create router
const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
    const publicPages = ['/'];
    const authRequired = !publicPages.includes(to.path);
    const loggedIn = api.isAuthenticated;

    if (authRequired && !loggedIn) {
        next('/');
    } else {
        next();
    }
});

// Create Vue app
const app = createApp(App);

// Use router
app.use(router);

// Mount app
app.mount('#app');