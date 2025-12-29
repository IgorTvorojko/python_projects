<template>
    <div class="game-container">
        <div class="game-header">
            <h1>{{ currentTournament?.name || 'Tournament' }}</h1>
            <div class="game-info">
                <span class="game-badge">{{ currentTournament?.game }}</span>
                <span class="status-badge" :class="currentTournament?.status">
                    {{ currentTournament?.status }}
                </span>
            </div>
        </div>

        <div class="game-content">
            <!-- Tournament Overview -->
            <div class="overview-section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-content">
                            <div class="stat-value">${{ currentTournament?.prize_pool || 0 }}</div>
                            <div class="stat-label">Prize Pool</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-content">
                            <div class="stat-value">{{ participants.length }}</div>
                            <div class="stat-label">Teams Registered</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📅</div>
                        <div class="stat-content">
                            <div class="stat-value">{{ matches.length }}</div>
                            <div class="stat-label">Total Matches</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🎮</div>
                        <div class="stat-content">
                            <div class="stat-value">{{ currentTournament?.max_teams || 0 }}</div>
                            <div class="stat-label">Max Teams</div>
                        </div>
                    </div>
                </div>

                <div class="description-box">
                    <h3>Description</h3>
                    <p>{{ currentTournament?.description || 'No description provided.' }}</p>
                </div>
            </div>

            <!-- Tabs Navigation -->
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

            <!-- Tab Content -->
            <div class="tab-content">
                <!-- Teams Tab -->
                <div v-if="activeTab === 'teams'" class="teams-tab">
                    <div class="section-header">
                        <h2>Registered Teams</h2>
                        <button 
                            v-if="canRegister && appState.user"
                            @click="showRegistrationModal = true"
                            class="btn-primary"
                        >
                            Register Team
                        </button>
                    </div>

                    <div v-if="participants.length === 0" class="empty-state">
                        <div class="empty-icon">👥</div>
                        <h3>No teams registered yet</h3>
                        <p v-if="canRegister">Be the first to register!</p>
                        <p v-else>Registration is closed</p>
                    </div>

                    <div v-else class="teams-grid">
                        <div v-for="participant in participants" :key="participant.id" class="team-card">
                            <div class="team-header">
                                <h3>{{ participant.team?.name || 'Unknown Team' }}</h3>
                                <span class="team-tag">{{ participant.team?.tag }}</span>
                            </div>
                            <div class="team-info">
                                <div class="info-row">
                                    <span class="info-label">Registered:</span>
                                    <span class="info-value">{{ formatDate(participant.registered_at) }}</span>
                                </div>
                                <div class="info-row" v-if="participant.final_position">
                                    <span class="info-label">Final Position:</span>
                                    <span class="info-value position">{{ getPositionText(participant.final_position) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Matches Tab -->
                <div v-else-if="activeTab === 'matches'" class="matches-tab">
                    <div class="section-header">
                        <h2>Tournament Matches</h2>
                        <button 
                            v-if="isOrganizer"
                            @click="showCreateMatchModal = true"
                            class="btn-primary"
                        >
                            Create Match
                        </button>
                    </div>

                    <div v-if="matches.length === 0" class="empty-state">
                        <div class="empty-icon">⚔️</div>
                        <h3>No matches scheduled</h3>
                        <p>Matches will appear here once they are created</p>
                    </div>

                    <div v-else class="matches-list">
                        <div v-for="match in matches" :key="match.id" class="match-card">
                            <div class="match-header">
                                <div class="match-round">Round {{ match.round }}</div>
                                <div class="match-status" :class="match.status">{{ match.status }}</div>
                            </div>
                            
                            <div class="teams-container">
                                <div class="team-display" :class="{ winner: match.winner_id === match.team1_id }">
                                    <div class="team-name">{{ getTeamName(match.team1_id) }}</div>
                                    <div class="team-score">{{ match.score1 }}</div>
                                </div>
                                
                                <div class="vs">VS</div>
                                
                                <div class="team-display" :class="{ winner: match.winner_id === match.team2_id }">
                                    <div class="team-name">{{ getTeamName(match.team2_id) }}</div>
                                    <div class="team-score">{{ match.score2 }}</div>
                                </div>
                            </div>
                            
                            <div class="match-info">
                                <div v-if="match.match_date" class="match-date">
                                    {{ formatDate(match.match_date) }}
                                </div>
                                <div v-if="isOrganizer" class="match-actions">
                                    <button 
                                        v-if="match.status !== 'completed'"
                                        @click="updateMatchScore(match)"
                                        class="btn-secondary"
                                    >
                                        Update Score
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Brackets Tab -->
                <div v-else-if="activeTab === 'brackets'" class="brackets-tab">
                    <div class="section-header">
                        <h2>Tournament Bracket</h2>
                    </div>
                    
                    <div class="bracket-container">
                        <div class="bracket-visualization">
                            <!-- Simple bracket visualization -->
                            <div class="bracket-round" v-for="round in bracketRounds" :key="round.number">
                                <h3>{{ round.name }}</h3>
                                <div class="bracket-matches">
                                    <div 
                                        v-for="match in round.matches" 
                                        :key="match.id"
                                        class="bracket-match"
                                        :class="match.status"
                                    >
                                        <div class="bracket-team">
                                            {{ match.team1 || 'TBD' }}
                                            <span class="bracket-score">{{ match.score1 }}</span>
                                        </div>
                                        <div class="bracket-team">
                                            {{ match.team2 || 'TBD' }}
                                            <span class="bracket-score">{{ match.score2 }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Registration Modal -->
        <div v-if="showRegistrationModal" class="modal-overlay" @click.self="closeRegistrationModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Register Team for Tournament</h3>
                    <button @click="closeRegistrationModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <div v-if="availableTeams.length === 0" class="no-teams">
                        <p>You need to create a team first before registering.</p>
                        <button @click="navigateToCreateTeam" class="btn-primary">Create Team</button>
                    </div>
                    <div v-else>
                        <div class="form-group">
                            <label>Select Team</label>
                            <select v-model="selectedTeamId" class="team-select">
                                <option value="">Choose a team</option>
                                <option v-for="team in availableTeams" :key="team.id" :value="team.id">
                                    {{ team.name }} ({{ team.tag }})
                                </option>
                            </select>
                        </div>
                        <div class="form-actions">
                            <button @click="closeRegistrationModal" class="btn-secondary">Cancel</button>
                            <button 
                                @click="registerTeam" 
                                :disabled="!selectedTeamId || isRegistering"
                                class="btn-primary"
                            >
                                <span v-if="isRegistering">Registering...</span>
                                <span v-else>Register</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Create Match Modal -->
        <div v-if="showCreateMatchModal" class="modal-overlay" @click.self="closeCreateMatchModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Create New Match</h3>
                    <button @click="closeCreateMatchModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="createMatch">
                        <div class="form-group">
                            <label>Round Number</label>
                            <input v-model="newMatch.round" type="number" min="1" required />
                        </div>
                        <div class="form-group">
                            <label>Team 1</label>
                            <select v-model="newMatch.team1_id" required>
                                <option value="">Select team</option>
                                <option v-for="team in participants" :key="team.team_id" :value="team.team_id">
                                    {{ team.team?.name }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Team 2</label>
                            <select v-model="newMatch.team2_id" required>
                                <option value="">Select team</option>
                                <option v-for="team in participants" :key="team.team_id" :value="team.team_id">
                                    {{ team.team?.name }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Match Date</label>
                            <input v-model="newMatch.match_date" type="datetime-local" />
                        </div>
                        <div class="form-actions">
                            <button type="button" @click="closeCreateMatchModal" class="btn-secondary">Cancel</button>
                            <button type="submit" :disabled="isCreatingMatch" class="btn-primary">
                                <span v-if="isCreatingMatch">Creating...</span>
                                <span v-else>Create Match</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Update Score Modal -->
        <div v-if="showUpdateScoreModal" class="modal-overlay" @click.self="closeUpdateScoreModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Update Match Score</h3>
                    <button @click="closeUpdateScoreModal" class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <div class="score-inputs">
                        <div class="team-score-input">
                            <div class="team-name">{{ getTeamName(editingMatch?.team1_id) }}</div>
                            <input v-model="score1" type="number" min="0" />
                        </div>
                        <div class="vs">VS</div>
                        <div class="team-score-input">
                            <div class="team-name">{{ getTeamName(editingMatch?.team2_id) }}</div>
                            <input v-model="score2" type="number" min="0" />
                        </div>
                    </div>
                    <div class="form-actions">
                        <button @click="closeUpdateScoreModal" class="btn-secondary">Cancel</button>
                        <button 
                            @click="submitScoreUpdate" 
                            :disabled="isUpdatingScore"
                            class="btn-primary"
                        >
                            <span v-if="isUpdatingScore">Updating...</span>
                            <span v-else>Update Score</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { appState, actions } from '../state';
import { api, Tournament, Team, Match, Participation } from '../api';

const route = useRoute();
const tournamentId = computed(() => parseInt(route.params.id as string));

// State
const activeTab = ref('teams');
const participants = ref<Participation[]>([]);
const matches = ref<Match[]>([]);
const availableTeams = ref<Team[]>([]);
const currentTournament = ref<Tournament | null>(null);

// Modal states
const showRegistrationModal = ref(false);
const showCreateMatchModal = ref(false);
const showUpdateScoreModal = ref(false);
const isRegistering = ref(false);
const isCreatingMatch = ref(false);
const isUpdatingScore = ref(false);

// Form data
const selectedTeamId = ref<number | null>(null);
const newMatch = ref({
    round: 1,
    team1_id: 0,
    team2_id: 0,
    match_date: '',
});
const editingMatch = ref<Match | null>(null);
const score1 = ref(0);
const score2 = ref(0);

const tabs = [
    { id: 'teams', label: 'Teams' },
    { id: 'matches', label: 'Matches' },
    { id: 'brackets', label: 'Bracket' },
];

const isOrganizer = computed(() => {
    return appState.user && currentTournament.value?.organizer_id === appState.user.id;
});

const canRegister = computed(() => {
    if (!currentTournament.value) return false;
    return currentTournament.value.status === 'upcoming';
});

const bracketRounds = computed(() => {
    // Simple bracket calculation based on matches
    const rounds: any[] = [];
    const maxRound = Math.max(...matches.value.map(m => m.round), 0);
    
    for (let i = 1; i <= maxRound; i++) {
        const roundMatches = matches.value.filter(m => m.round === i);
        rounds.push({
            number: i,
            name: i === maxRound ? 'Final' : i === maxRound - 1 ? 'Semi-finals' : `Round ${i}`,
            matches: roundMatches.map(match => ({
                ...match,
                team1: getTeamName(match.team1_id),
                team2: getTeamName(match.team2_id),
            })),
        });
    }
    
    return rounds;
});

onMounted(async () => {
    await loadTournamentData();
    await loadAvailableTeams();
});

async function loadTournamentData() {
    try {
        // Load tournament details
        currentTournament.value = await api.getTournament(tournamentId.value);
        
        // Load participants
        participants.value = await actions.loadTournamentParticipants(tournamentId.value);
        
        // Load matches for this tournament
        // Note: You would need to implement this endpoint in your API
        // For now, we'll filter from global state
        matches.value = appState.matches.filter(m => m.tournament_id === tournamentId.value);
    } catch (error) {
        console.error('Failed to load tournament data:', error);
    }
}

async function loadAvailableTeams() {
    try {
        await actions.loadTeams();
        availableTeams.value = appState.teams.filter(team => 
            !participants.value.some(p => p.team_id === team.id)
        );
    } catch (error) {
        console.error('Failed to load available teams:', error);
    }
}

function getTeamName(teamId: number): string {
    const team = appState.teams.find(t => t.id === teamId);
    return team?.name || `Team ${teamId}`;
}

function getPositionText(position: number): string {
    if (position === 1) return '1st 🥇';
    if (position === 2) return '2nd 🥈';
    if (position === 3) return '3rd 🥉';
    return `${position}th`;
}

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// Registration
function openRegistrationModal() {
    showRegistrationModal.value = true;
}

function closeRegistrationModal() {
    showRegistrationModal.value = false;
    selectedTeamId.value = null;
}

async function registerTeam() {
    if (!selectedTeamId.value) return;

    isRegistering.value = true;
    try {
        await actions.registerTeamForTournament(tournamentId.value, selectedTeamId.value);
        await loadTournamentData();
        await loadAvailableTeams();
        closeRegistrationModal();
        alert('Team registered successfully!');
    } catch (error: any) {
        alert(error.message || 'Failed to register team');
    } finally {
        isRegistering.value = false;
    }
}

function navigateToCreateTeam() {
    closeRegistrationModal();
    // Navigate to team creation - implement as needed
    alert('Navigate to team creation page');
}

// Matches
function openCreateMatchModal() {
    showCreateMatchModal.value = true;
}

function closeCreateMatchModal() {
    showCreateMatchModal.value = false;
    newMatch.value = {
        round: 1,
        team1_id: 0,
        team2_id: 0,
        match_date: '',
    };
}

async function createMatch() {
    if (!newMatch.value.team1_id || !newMatch.value.team2_id) {
        alert('Please select both teams');
        return;
    }

    if (newMatch.value.team1_id === newMatch.value.team2_id) {
        alert('Teams cannot play against themselves');
        return;
    }

    isCreatingMatch.value = true;
    try {
        const matchData = {
            ...newMatch.value,
            tournament_id: tournamentId.value,
        };
        
        const match = await api.createMatch(matchData);
        matches.value.push(match);
        closeCreateMatchModal();
        alert('Match created successfully!');
    } catch (error) {
        console.error('Failed to create match:', error);
        alert('Failed to create match');
    } finally {
        isCreatingMatch.value = false;
    }
}

function updateMatchScore(match: Match) {
    editingMatch.value = match;
    score1.value = match.score1;
    score2.value = match.score2;
    showUpdateScoreModal.value = true;
}

function closeUpdateScoreModal() {
    showUpdateScoreModal.value = false;
    editingMatch.value = null;
    score1.value = 0;
    score2.value = 0;
}

async function submitScoreUpdate() {
    if (!editingMatch.value) return;

    isUpdatingScore.value = true;
    try {
        const updatedMatch = await api.updateMatchScore(
            editingMatch.value.id,
            score1.value,
            score2.value
        );
        
        // Update local matches list
        const index = matches.value.findIndex(m => m.id === editingMatch.value!.id);
        if (index !== -1) {
            matches.value[index] = updatedMatch;
        }
        
        closeUpdateScoreModal();
        alert('Score updated successfully!');
    } catch (error) {
        console.error('Failed to update score:', error);
        alert('Failed to update score');
    } finally {
        isUpdatingScore.value = false;
    }
}
</script>

<style scoped>
.game-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.game-header {
    text-align: center;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.game-header h1 {
    font-size: 2.5rem;
    color: #fff;
    margin-bottom: 1rem;
}

.game-info {
    display: flex;
    gap: 1rem;
    justify-content: center;
    align-items: center;
}

.game-badge {
    background: linear-gradient(45deg, #00ff88, #00ccff);
    color: #000;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.upcoming {
    background: #00ff88;
    color: #000;
}

.status-badge.ongoing {
    background: #ffcc00;
    color: #000;
}

.status-badge.completed {
    background: #ff6b00;
    color: #000;
}

.game-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.overview-section {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.3s;
}

.stat-card:hover {
    transform: translateY(-3px);
}

.stat-icon {
    font-size: 2rem;
    opacity: 0.8;
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #fff;
    margin-bottom: 0.25rem;
}

.stat-label {
    color: #aaa;
    font-size: 0.9rem;
}

.description-box {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
}

.description-box h3 {
    color: #fff;
    margin-bottom: 1rem;
}

.description-box p {
    color: #ccc;
    line-height: 1.6;
}

.tabs {
    display: flex;
    gap: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.5rem;
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

.tab-content {
    min-height: 400px;
}

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

.teams-grid, .matches-list {
    display: grid;
    gap: 1rem;
}

.team-card, .match-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s, border-color 0.3s;
}

.team-card:hover, .match-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 255, 136, 0.3);
}

.team-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.team-header h3 {
    color: #fff;
    margin: 0;
    font-size: 1.2rem;
}

.team-tag {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
}

.team-info {
    display: grid;
    gap: 0.5rem;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-label {
    color: #aaa;
    font-size: 0.9rem;
}

.info-value {
    color: #fff;
    font-weight: 500;
}

.info-value.position {
    color: gold;
    font-weight: bold;
}

.match-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.match-round {
    color: #00ff88;
    font-weight: 600;
    font-size: 1.1rem;
}

.match-status {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.match-status.scheduled {
    background: rgba(0, 150, 255, 0.2);
    color: #0096ff;
}

.match-status.ongoing {
    background: rgba(255, 204, 0, 0.2);
    color: #ffcc00;
}

.match-status.completed {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
}

.teams-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    margin-bottom: 1.5rem;
}

.team-display {
    flex: 1;
    text-align: center;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    border: 2px solid transparent;
    transition: border-color 0.3s;
}

.team-display.winner {
    border-color: #00ff88;
}

.team-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 0.5rem;
}

.team-score {
    font-size: 2rem;
    font-weight: bold;
    color: #00ff88;
}

.vs {
    color: #aaa;
    font-weight: 600;
    font-size: 1.2rem;
}

.match-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.match-date {
    color: #aaa;
    font-size: 0.9rem;
}

.match-actions {
    display: flex;
    gap: 0.5rem;
}

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

.bracket-container {
    overflow-x: auto;
}

.bracket-visualization {
    display: flex;
    gap: 3rem;
    padding: 2rem 0;
    min-width: 800px;
}

.bracket-round {
    flex: 1;
}

.bracket-round h3 {
    color: #fff;
    text-align: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.bracket-matches {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.bracket-match {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.bracket-match.scheduled {
    opacity: 0.7;
}

.bracket-match.completed {
    border-color: rgba(0, 255, 136, 0.3);
}

.bracket-team {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    color: #fff;
}

.bracket-team:first-child {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 0.5rem;
}

.bracket-score {
    color: #00ff88;
    font-weight: bold;
}

.score-inputs {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    margin: 2rem 0;
}

.team-score-input {
    flex: 1;
    text-align: center;
}

.team-score-input .team-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 1rem;
}

.team-score-input input {
    width: 100px;
    height: 60px;
    font-size: 2rem;
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
    border: 2px solid #444;
    border-radius: 10px;
    color: #fff;
}

.team-score-input input:focus {
    border-color: #00ff88;
    outline: none;
}

.no-teams {
    text-align: center;
    padding: 2rem;
}

.no-teams p {
    color: #aaa;
    margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
    .game-container {
        padding: 1rem;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
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
    
    .teams-container {
        flex-direction: column;
        gap: 1rem;
    }
    
    .match-info {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .score-inputs {
        flex-direction: column;
        gap: 1rem;
    }
}
</style>