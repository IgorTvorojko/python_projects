<template>
    <div class="profile-container">
        <div class="profile-header">
            <div class="avatar">
                <div class="avatar-circle">
                    {{ userInitials }}
                </div>
            </div>
            <div class="profile-info">
                <h1>{{ appState.user?.full_name || appState.user?.username }}</h1>
                <p class="username">@{{ appState.user?.username }}</p>
                <div class="profile-stats">
                    <div class="stat">
                        <div class="stat-number">{{ tournamentsCount }}</div>
                        <div class="stat-label">Tournaments</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{ teamsCount }}</div>
                        <div class="stat-label">Teams</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{ participationsCount }}</div>
                        <div class="stat-label">Participations</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="profile-content">
            <div class="tabs">
                <button 
                    v-for="tab in tabs" 
                    :key="tab.id"
                    @click="activeTab = tab.id"
                    :class="['tab-button', { active: activeTab === tab.id }]"
                >
                    {{ tab.label }}
                </button>
            </div>

            <div class="tab-content">
                <!-- Overview Tab -->
                <div v-if="activeTab === 'overview'" class="overview-tab">
                    <div class="info-section">
                        <h2>Personal Information</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Email</label>
                                <div class="info-value">{{ appState.user?.email }}</div>
                            </div>
                            <div class="info-item">
                                <label>Full Name</label>
                                <div class="info-value">{{ appState.user?.full_name || 'Not set' }}</div>
                            </div>
                            <div class="info-item">
                                <label>Member Since</label>
                                <div class="info-value">{{ joinDate }}</div>
                            </div>
                            <div class="info-item">
                                <label>Status</label>
                                <div class="info-value status" :class="appState.user?.is_active ? 'active' : 'inactive'">
                                    {{ appState.user?.is_active ? 'Active' : 'Inactive' }}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bio-section" v-if="appState.user?.bio">
                        <h2>Bio</h2>
                        <div class="bio-content">
                            {{ appState.user.bio }}
                        </div>
                    </div>
                </div>

                <!-- My Tournaments Tab -->
                <div v-else-if="activeTab === 'tournaments'" class="tournaments-tab">
                    <div class="section-header">
                        <h2>My Tournaments</h2>
                        <button @click="refreshData" class="btn-secondary">
                            Refresh
                        </button>
                    </div>

                    <div v-if="myTournaments.length === 0" class="empty-state">
                        <div class="empty-icon">🏆</div>
                        <h3>No tournaments yet</h3>
                        <p>Create your first tournament to get started!</p>
                        <button @click="navigateToHost" class="btn-primary">
                            Create Tournament
                        </button>
                    </div>

                    <div v-else class="tournaments-list">
                        <div v-for="tournament in myTournaments" :key="tournament.id" class="tournament-item">
                            <div class="tournament-main">
                                <h3>{{ tournament.name }}</h3>
                                <div class="tournament-meta">
                                    <span class="game-badge">{{ tournament.game }}</span>
                                    <span class="status-badge" :class="tournament.status">
                                        {{ tournament.status }}
                                    </span>
                                </div>
                            </div>
                            <div class="tournament-details">
                                <div class="detail">
                                    <span class="detail-label">Teams:</span>
                                    <span class="detail-value">{{ tournament.max_teams }}</span>
                                </div>
                                <div class="detail">
                                    <span class="detail-label">Prize:</span>
                                    <span class="detail-value prize">${{ tournament.prize_pool }}</span>
                                </div>
                                <div class="detail">
                                    <span class="detail-label">Created:</span>
                                    <span class="detail-value">{{ formatDate(tournament.created_at) }}</span>
                                </div>
                            </div>
                            <div class="tournament-actions">
                                <button @click="viewTournament(tournament.id)" class="btn-secondary">
                                    View
                                </button>
                                <button 
                                    v-if="tournament.status === 'upcoming'"
                                    @click="editTournament(tournament)"
                                    class="btn-primary"
                                >
                                    Edit
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- My Teams Tab -->
                <div v-else-if="activeTab === 'teams'" class="teams-tab">
                    <div class="section-header">
                        <h2>My Teams</h2>
                        <button @click="showCreateTeamModal = true" class="btn-primary">
                            Create Team
                        </button>
                    </div>

                    <div v-if="myTeams.length === 0" class="empty-state">
                        <div class="empty-icon">👥</div>
                        <h3>No teams yet</h3>
                        <p>Create your first team to participate in tournaments!</p>
                    </div>

                    <div v-else class="teams-list">
                        <div v-for="team in myTeams" :key="team.id" class="team-item">
                            <div class="team-main">
                                <h3>{{ team.name }}</h3>
                                <span class="team-tag">{{ team.tag }}</span>
                            </div>
                            <div class="team-details">
                                <div class="detail">
                                    <span class="detail-label">Created:</span>
                                    <span class="detail-value">{{ formatDate(team.created_at) }}</span>
                                </div>
                                <div class="detail" v-if="team.description">
                                    <span class="detail-label">Description:</span>
                                    <span class="detail-value description">{{ team.description }}</span>
                                </div>
                            </div>
                            <div class="team-actions">
                                <button @click="viewTeam(team.id)" class="btn-secondary">
                                    View
                                </button>
                                <button @click="editTeam(team)" class="btn-primary">
                                    Edit
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Settings Tab -->
                <div v-else-if="activeTab === 'settings'" class="settings-tab">
                    <div class="settings-section">
                        <h2>Account Settings</h2>
                        
                        <div class="settings-form">
                            <div class="form-group">
                                <label>Full Name</label>
                                <input 
                                    v-model="settings.full_name" 
                                    type="text" 
                                    placeholder="Enter your full name"
                                />
                            </div>
                            
                            <div class="form-group">
                                <label>Bio</label>
                                <textarea 
                                    v-model="settings.bio" 
                                    rows="4" 
                                    placeholder="Tell us about yourself..."
                                ></textarea>
                            </div>
                            
                            <div class="form-actions">
                                <button @click="resetSettings" class="btn-secondary">
                                    Reset
                                </button>
                                <button 
                                    @click="saveSettings" 
                                    :disabled="isSaving"
                                    class="btn-primary"
                                >
                                    <span v-if="isSaving">Saving...</span>
                                    <span v-else>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="danger-zone">
                        <h2>Danger Zone</h2>
                        <div class="danger-actions">
                            <button @click="changePassword" class="btn-secondary">
                                Change Password
                            </button>
                            <button @click="logout" class="btn-danger">
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Create Team Modal -->
        <div v-if="showCreateTeamModal" class="modal-overlay" @click.self="closeCreateTeamModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Create New Team</h3>
                    <button @click="closeCreateTeamModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="createTeam">
                        <div class="form-group">
                            <label>Team Name *</label>
                            <input v-model="newTeam.name" type="text" required placeholder="e.g., Cyber Warriors" />
                        </div>
                        <div class="form-group">
                            <label>Team Tag</label>
                            <input v-model="newTeam.tag" type="text" placeholder="e.g., CW" maxlength="10" />
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea v-model="newTeam.description" rows="3" placeholder="Describe your team..."></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" @click="closeCreateTeamModal" class="btn-secondary">Cancel</button>
                            <button type="submit" :disabled="isCreatingTeam" class="btn-primary">
                                <span v-if="isCreatingTeam">Creating...</span>
                                <span v-else>Create Team</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Edit Team Modal -->
        <div v-if="showEditTeamModal" class="modal-overlay" @click.self="closeEditTeamModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Edit Team</h3>
                    <button @click="closeEditTeamModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="updateTeam">
                        <div class="form-group">
                            <label>Team Name *</label>
                            <input v-model="editingTeam.name" type="text" required />
                        </div>
                        <div class="form-group">
                            <label>Team Tag</label>
                            <input v-model="editingTeam.tag" type="text" maxlength="10" />
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea v-model="editingTeam.description" rows="3"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" @click="closeEditTeamModal" class="btn-secondary">Cancel</button>
                            <button type="submit" :disabled="isUpdatingTeam" class="btn-primary">
                                <span v-if="isUpdatingTeam">Updating...</span>
                                <span v-else>Update Team</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { appState, mutations, actions } from '../state';
import { api, Team } from '../api';

const router = useRouter();

// State
const activeTab = ref('overview');
const isSaving = ref(false);
const isCreatingTeam = ref(false);
const isUpdatingTeam = ref(false);
const showCreateTeamModal = ref(false);
const showEditTeamModal = ref(false);

// Form data
const settings = ref({
    full_name: appState.user?.full_name || '',
    bio: appState.user?.bio || '',
});
const newTeam = ref({
    name: '',
    tag: '',
    description: '',
});
const editingTeam = ref<Team | null>(null);

const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'tournaments', label: 'My Tournaments' },
    { id: 'teams', label: 'My Teams' },
    { id: 'settings', label: 'Settings' },
];

const userInitials = computed(() => {
    const name = appState.user?.full_name || appState.user?.username || '';
    return name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
});

const joinDate = computed(() => {
    if (!appState.user?.created_at) return '';
    return new Date(appState.user.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
});

const tournamentsCount = computed(() => {
    return appState.tournaments.filter(t => 
        appState.user && t.organizer_id === appState.user.id
    ).length;
});

const teamsCount = computed(() => {
    return appState.teams.length;
});

const participationsCount = computed(() => {
    // This would need an API endpoint to get user's participations
    // For now, we'll return a placeholder
    return 0;
});

const myTournaments = computed(() => {
    return appState.tournaments.filter(t => 
        appState.user && t.organizer_id === appState.user.id
    );
});

const myTeams = computed(() => {
    return appState.teams;
});

onMounted(async () => {
    await refreshData();
});

async function refreshData() {
    await actions.loadTournaments();
    await actions.loadTeams();
}

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

// Navigation
function navigateToHost() {
    router.push('/host');
}

function viewTournament(id: number) {
    router.push(`/game/${id}`);
}

function editTournament(tournament: any) {
    // Navigate to tournament edit or open modal
    alert(`Edit tournament ${tournament.id} - Implement edit functionality`);
}

function viewTeam(id: number) {
    // Implement team view
    alert(`View team ${id} - Implement team view`);
}

function editTeam(team: Team) {
    editingTeam.value = { ...team };
    showEditTeamModal.value = true;
}

// Settings
function resetSettings() {
    settings.value = {
        full_name: appState.user?.full_name || '',
        bio: appState.user?.bio || '',
    };
}

async function saveSettings() {
    isSaving.value = true;
    try {
        // Note: You would need to implement an update user endpoint in your API
        // For now, we'll just update the local state
        if (appState.user) {
            mutations.setUser({
                ...appState.user,
                full_name: settings.value.full_name,
                bio: settings.value.bio,
            });
        }
        alert('Settings saved successfully!');
    } catch (error) {
        console.error('Failed to save settings:', error);
        alert('Failed to save settings');
    } finally {
        isSaving.value = false;
    }
}

function changePassword() {
    alert('Change password functionality - To be implemented');
}

function logout() {
    actions.logout();
    router.push('/');
}

// Team Management
function openCreateTeamModal() {
    showCreateTeamModal.value = true;
}

function closeCreateTeamModal() {
    showCreateTeamModal.value = false;
    newTeam.value = {
        name: '',
        tag: '',
        description: '',
    };
}

function closeEditTeamModal() {
    showEditTeamModal.value = false;
    editingTeam.value = null;
}

async function createTeam() {
    if (!newTeam.value.name.trim()) {
        alert('Please enter a team name');
        return;
    }

    isCreatingTeam.value = true;
    try {
        const team = await actions.createTeam(newTeam.value);
        closeCreateTeamModal();
        alert('Team created successfully!');
    } catch (error) {
        console.error('Failed to create team:', error);
        alert('Failed to create team');
    } finally {
        isCreatingTeam.value = false;
    }
}

async function updateTeam() {
    if (!editingTeam.value) return;

    isUpdatingTeam.value = true;
    try {
        // Note: You would need to implement an update team endpoint in your API
        // For now, we'll just update the local state
        mutations.updateTeam(editingTeam.value);
        closeEditTeamModal();
        alert('Team updated successfully!');
    } catch (error) {
        console.error('Failed to update team:', error);
        alert('Failed to update team');
    } finally {
        isUpdatingTeam.value = false;
    }
}
</script>

<style scoped>
.profile-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.profile-header {
    display: flex;
    gap: 2rem;
    align-items: center;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar-circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(45deg, #00ff88, #00ccff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    font-weight: bold;
    color: #000;
}

.profile-info {
    flex: 1;
}

.profile-info h1 {
    font-size: 2.5rem;
    color: #fff;
    margin-bottom: 0.5rem;
}

.username {
    color: #aaa;
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
}

.profile-stats {
    display: flex;
    gap: 3rem;
}

.stat {
    text-align: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #00ff88;
    margin-bottom: 0.25rem;
}

.stat-label {
    color: #aaa;
    font-size: 0.9rem;
}

.profile-content {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.tabs {
    display: flex;
    gap: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.5rem;
    margin-bottom: 2rem;
}

.tab-button {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    color: #aaa;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    border-radius: 8px 8px 0 0;
    transition: all 0.3s;
}

.tab-button:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
}

.tab-button.active {
    background: rgba(0, 255, 136, 0.1);
    color: #00ff88;
    border-bottom: 2px solid #00ff88;
}

/* Overview Tab */
.overview-tab {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.info-section h2,
.bio-section h2 {
    color: #fff;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.info-item label {
    color: #aaa;
    font-size: 0.9rem;
    font-weight: 500;
}

.info-value {
    color: #fff;
    font-size: 1.1rem;
}

.info-value.status {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    display: inline-block;
    font-weight: 600;
}

.info-value.status.active {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
}

.info-value.status.inactive {
    background: rgba(255, 59, 48, 0.2);
    color: #ff3b30;
}

.bio-content {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    padding: 1.5rem;
    color: #ccc;
    line-height: 1.6;
}

/* Tournaments Tab */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.section-header h2 {
    color: #fff;
    margin: 0;
}

.tournaments-list,
.teams-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.tournament-item,
.team-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s, border-color 0.3s;
}

.tournament-item:hover,
.team-item:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 255, 136, 0.3);
}

.tournament-main,
.team-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.tournament-main h3,
.team-main h3 {
    color: #fff;
    margin: 0;
    font-size: 1.2rem;
}

.tournament-meta {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

.game-badge {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.upcoming {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
}

.status-badge.ongoing {
    background: rgba(255, 204, 0, 0.2);
    color: #ffcc00;
}

.status-badge.completed {
    background: rgba(255, 107, 0, 0.2);
    color: #ff6b00;
}

.team-tag {
    background: rgba(0, 150, 255, 0.2);
    color: #0096ff;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
}

.tournament-details,
.team-details {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.detail {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.detail-label {
    color: #aaa;
    font-size: 0.9rem;
}

.detail-value {
    color: #fff;
    font-weight: 500;
}

.detail-value.prize {
    color: gold;
}

.detail-value.description {
    color: #ccc;
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tournament-actions,
.team-actions {
    display: flex;
    gap: 0.75rem;
}

/* Settings Tab */
.settings-section {
    margin-bottom: 3rem;
}

.settings-section h2 {
    color: #fff;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

.settings-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.settings-form .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.settings-form label {
    color: #00ff88;
    font-weight: 500;
    font-size: 0.9rem;
}

.settings-form input,
.settings-form textarea {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid #444;
    border-radius: 8px;
    padding: 0.75rem;
    color: #fff;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.settings-form input:focus,
.settings-form textarea:focus {
    outline: none;
    border-color: #00ff88;
}

.settings-form input::placeholder,
.settings-form textarea::placeholder {
    color: #666;
}

.settings-form .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
}

.danger-zone {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 2rem;
}

.danger-zone h2 {
    color: #ff3b30;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

.danger-actions {
    display: flex;
    gap: 1rem;
}

/* Common button styles */
.btn-primary, .btn-secondary, .btn-danger {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1rem;
}

.btn-primary {
    background: linear-gradient(45deg, #00ff88, #00ccff);
    color: #000;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
}

.btn-danger {
    background: rgba(255, 59, 48, 0.2);
    color: #ff3b30;
    border: 1px solid rgba(255, 59, 48, 0.3);
}

.btn-danger:hover {
    background: rgba(255, 59, 48, 0.3);
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #aaa;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-state h3 {
    color: #fff;
    margin-bottom: 0.5rem;
}

.empty-state p {
    margin-bottom: 1.5rem;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(5px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal {
    background: #1a1a1a;
    border-radius: 15px;
    width: 90%;
    max-width: 500px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
    color: #fff;
    margin: 0;
}

.modal-close {
    background: none;
    border: none;
    color: #fff;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.3s;
}

.modal-close:hover {
    background: rgba(255, 255, 255, 0.1);
}

.modal-body {
    padding: 1.5rem;
}

@media (max-width: 768px) {
    .profile-container {
        padding: 1rem;
    }
    
    .profile-header {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    
    .avatar-circle {
        width: 80px;
        height: 80px;
        font-size: 2rem;
    }
    
    .profile-stats {
        justify-content: center;
        gap: 2rem;
    }
    
    .tabs {
        overflow-x: auto;
        white-space: nowrap;
    }
    
    .section-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .tournament-details,
    .team-details {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .tournament-actions,
    .team-actions {
        flex-direction: column;
    }
    
    .danger-actions {
        flex-direction: column;
    }
}
</style>