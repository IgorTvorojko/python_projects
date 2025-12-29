<template>
    <div id="app">
        <nav class="navbar">
            <router-link to="/" class="logo">
                CYBER TOURNAMENT
            </router-link>
            <div class="nav-links">
                <router-link to="/">Home</router-link>
                <router-link to="/tournaments">Tournaments</router-link>
                <router-link to="/host" v-if="isAuthenticated">Host</router-link>
                <router-link to="/profile" v-if="isAuthenticated">Profile</router-link>
                <router-link to="/login" v-if="!isAuthenticated">Login</router-link>
                <router-link to="/register" v-if="!isAuthenticated">Register</router-link>
                <a href="#" @click.prevent="logout" v-if="isAuthenticated">Logout</a>
            </div>
        </nav>
        
        <main class="main-content">
            <router-view />
        </main>
        
        <footer class="footer">
            <p>&copy; 2024 Cyber Tournament Platform. All rights reserved.</p>
        </footer>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { appState, actions } from './state';

const router = useRouter();

const isAuthenticated = computed(() => appState.user !== null);

function logout() {
    actions.logout();
    router.push('/');
}
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #fff;
    min-height: 100vh;
}

#app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.navbar {
    background: rgba(0, 0, 0, 0.8);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 100;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #00ff88;
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-links a {
    color: #fff;
    text-decoration: none;
    transition: color 0.3s;
    font-weight: 500;
}

.nav-links a:hover {
    color: #00ff88;
}

.nav-links a.router-link-active {
    color: #00ff88;
    border-bottom: 2px solid #00ff88;
}

.main-content {
    flex: 1;
    padding: 2rem;
}

.footer {
    background: rgba(0, 0, 0, 0.8);
    padding: 1.5rem;
    text-align: center;
    color: #aaa;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer p {
    margin: 0;
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
    }
    
    .nav-links {
        flex-wrap: wrap;
        justify-content: center;
        gap: 1rem;
    }
    
    .main-content {
        padding: 1rem;
    }
}
</style>