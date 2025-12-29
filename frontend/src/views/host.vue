<template>
    <div class="host-container">
        <div class="header">
            <h1>Host Tournament</h1>
            <p>Create and manage your esports tournaments</p>
        </div>

        <div class="content">
            <div class="create-section">
                <h2>Create New Tournament</h2>
                <form @submit.prevent="createTournament" class="tournament-form">
                    <div class="form-group">
                        <label for="tournament-name">Tournament Name *</label>
                        <input
                            id="tournament-name"
                            v-model="newTournament.name"
                            type="text"
                            required
                            placeholder="e.g., CS:GO Championship 2024"
                        />
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="game">Game *</label>
                            <select id="game" v-model="newTournament.game" required>
                                <option value="CS:GO">CS:GO</option>
                                <option value="Dota 2">Dota 2</option>
                                <option value="Valorant">Valorant</option>
                                <option value="League of Legends">League of Legends</option>
                                <option value="Overwatch 2">Overwatch 2</option>
                                <option value="Rainbow Six Siege">Rainbow Six Siege</option>
                                <option value="PUBG">PUBG</option>
                                <option value="Fortnite">Fortnite</option>
                                <option value="Apex Legends">Apex Legends</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="max-teams">Max Teams *</label>
                            <input
                                id="max-teams"
                                v-model="newTournament.max_teams"
                                type="number"
                                min="2"
                                max="64"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="prize-pool">Prize Pool ($)</label>
                            <input
                                id="prize-pool"
                                v-model="newTournament.prize_pool"
                                type="number"
                                min="0"
                                placeholder="0"
                            />
                        </div>

                        <div class="form-group">
                            <label for="start-date">Start Date</label>
                            <input
                                id="start-date"
                                v-model="newTournament.start_date"
                                type="datetime-local"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="description">Description</label>
                        <textarea
                            id="description"
                            v-model="newTournament.description"
                            rows="3"
                            placeholder="Describe your tournament, rules, format, etc."
                        ></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="submit" :disabled="isCreating" class="btn-primary">
                            <span v-if="isCreating">Creating...</span>
                            <span v-else>Create Tournament</span>
                        </button>
                    </div>
                </form>
            </div>

            <div class="my-tournaments-section" v-if="myTournaments.length > 0">
                <h2>My Tournaments</h2>
                <div class="tournaments-grid">
                    <div v-for="tournament in myTournaments" :key="tournament.id" class="tournament-card">
                        <div class="tournament-header">
                            <h3>{{ tournament.name }}</h3>
                            <span class="game-badge" :class="getGameClass(tournament.game)">
                                {{ tournament.game }}
                            </span>
                        </div>
                        
                        <div class="tournament-info">
                            <div class="info-row">
                                <span class="info-label">Status:</span>
                                <span class="info-value" :class="getStatusClass(tournament.status)">
                                    {{ tournament.status }}
                                </span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Teams:</span>
                                <span class="info-value">{{ tournament.max_teams }} max</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Prize Pool:</span>
                                <span class="info-value prize">${{ tournament.prize_pool }}</span>
                            </div>
                            <div class="info-row" v-if="tournament.start_date">
                                <span class="info-label">Starts:</span>
                                <span class="info-value">{{ formatDate(tournament.start_date) }}</span>
                            </div>
                        </div>

                        <div class="tournament-actions">
                            <button @click="editTournament(tournament)" class="btn-secondary">Edit</button>
                            <button @click="viewTournament(tournament.id)" class="btn-primary">View Details</button>
                            <button @click="deleteTournament(tournament.id)" class="btn-danger">Delete</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="empty-state" v-else>
                <div class="empty-icon">🏆</div>
                <h3>No tournaments yet</h3>
                <p>Create your first tournament to get started!</p>
            </div>
        </div>

        <!-- Edit Modal -->
        <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Edit Tournament</h3>
                    <button @click="closeEditModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="updateTournament">
                        <div class="form-group">
                            <label>Name</label>
                            <input v-model="editingTournament.name" type="text" required />
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea v-model="editingTournament.description" rows="3"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" @click="closeEditModal" class="btn-secondary">Cancel</button>
                            <button type="submit" :disabled="isUpdating" class="btn-primary">
                                <span v-if="isUpdating">Updating...</span>
                                <span v-else>Update</span>
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
import { appState, mutations, actions } from '../state';
import { Tournament } from '../api';

const newTournament = ref({
    name: '',
    game: 'CS:GO',
    description: '',
    max_teams: 16,
    prize_pool: 0,
    start_date: '',
});

const isCreating = ref(false);
const isUpdating = ref(false);
const showEditModal = ref(false);
const editingTournament = ref<Tournament | null>(null);

const myTournaments = computed(() => {
    return appState.tournaments.filter(t => 
        appState.user && t.organizer_id === appState.user.id
    );
});

onMounted(async () => {
    await actions.loadTournaments();
});

const getGameClass = (game: string) => {
    const classes: { [key: string]: string } = {
        'CS:GO': 'csgo',
        'Dota 2': 'dota',
        'Valorant': 'valorant',
        'League of Legends': 'lol',
        'Overwatch 2': 'ow',
    };
    return classes[game] || 'default';
};

const getStatusClass = (status: string) => {
    const classes: { [key: string]: string } = {
        'upcoming': 'upcoming',
        'ongoing': 'ongoing',
        'completed': 'completed',
    };
    return classes[status] || 'default';
};

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};

async function createTournament() {
    if (!newTournament.value.name.trim()) {
        alert('Please enter a tournament name');
        return;
    }

    isCreating.value = true;
    try {
        await actions.createTournament(newTournament.value);
        
        // Reset form
        newTournament.value = {
            name: '',
            game: 'CS:GO',
            description: '',
            max_teams: 16,
            prize_pool: 0,
            start_date: '',
        };

        alert('Tournament created successfully!');
    } catch (error) {
        console.error('Failed to create tournament:', error);
    } finally {
        isCreating.value = false;
    }
}

function editTournament(tournament: Tournament) {
    editingTournament.value = { ...tournament };
    showEditModal.value = true;
}

async function updateTournament() {
    if (!editingTournament.value) return;

    isUpdating.value = true;
    try {
        const updated = await api.updateTournament(
            editingTournament.value.id,
            {
                name: editingTournament.value.name,
                description: editingTournament.value.description,
            }
        );
        
        mutations.updateTournament(updated);
        closeEditModal();
        alert('Tournament updated successfully!');
    } catch (error) {
        console.error('Failed to update tournament:', error);
        alert('Failed to update tournament');
    } finally {
        isUpdating.value = false;
    }
}

function closeEditModal() {
    showEditModal.value = false;
    editingTournament.value = null;
}

async function deleteTournament(id: number) {
    if (!confirm('Are you sure you want to delete this tournament?')) {
        return;
    }

    try {
        await api.deleteTournament(id);
        mutations.removeTournament(id);
        alert('Tournament deleted successfully!');
    } catch (error) {
        console.error('Failed to delete tournament:', error);
        alert('Failed to delete tournament');
    }
}

function viewTournament(id: number) {
    // This would navigate to tournament details page
    alert(`Viewing tournament ${id} - Implement navigation`);
}
</script>

<style scoped>
.host-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.header {
    text-align: center;
    margin-bottom: 3rem;
}

.header h1 {
    font-size: 2.5rem;
    color: #fff;
    margin-bottom: 0.5rem;
}

.header p {
    color: #aaa;
    font-size: 1.1rem;
}

.content {
    display: grid;
    gap: 3rem;
}

.create-section, .my-tournaments-section {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

h2 {
    color: #fff;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

.tournament-form {
    display: grid;
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

label {
    color: #00ff88;
    font-weight: 500;
    font-size: 0.9rem;
}

input, select, textarea {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid #444;
    border-radius: 8px;
    padding: 0.75rem;
    color: #fff;
    font-size: 1rem;
    transition: border-color 0.3s;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #00ff88;
}

input::placeholder, textarea::placeholder {
    color: #666;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
}

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

.tournaments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.tournament-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s, border-color 0.3s;
}

.tournament-card:hover {
    transform: translateY(-5px);
    border-color: #00ff88;
}

.tournament-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.tournament-header h3 {
    color: #fff;
    font-size: 1.2rem;
    margin: 0;
    flex: 1;
}

.game-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.game-badge.csgo { background: #ff6b00; color: #000; }
.game-badge.dota { background: #d32f2f; color: #fff; }
.game-badge.valorant { background: #fa4454; color: #fff; }
.game-badge.lol { background: #005aff; color: #fff; }
.game-badge.ow { background: #f99e1a; color: #000; }
.game-badge.default { background: #666; color: #fff; }

.tournament-info {
    margin-bottom: 1.5rem;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    color: #aaa;
    font-size: 0.9rem;
}

.info-value {
    color: #fff;
    font-weight: 500;
}

.info-value.prize {
    color: gold;
}

.info-value.upcoming { color: #00ff88; }
.info-value.ongoing { color: #ffcc00; }
.info-value.completed { color: #ff6b00; }

.tournament-actions {
    display: flex;
    gap: 0.75rem;
}

.tournament-actions button {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.9rem;
}

.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #aaa;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.empty-state h3 {
    color: #fff;
    margin-bottom: 0.5rem;
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
    .host-container {
        padding: 1rem;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .tournaments-grid {
        grid-template-columns: 1fr;
    }
    
    .tournament-actions {
        flex-direction: column;
    }
}
</style>