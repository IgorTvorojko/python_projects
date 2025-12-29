import { reactive, readonly } from 'vue';
import { api, User, Tournament, Team, Match } from './api';

interface AppState {
    user: User | null;
    tournaments: Tournament[];
    teams: Team[];
    matches: Match[];
    isLoading: boolean;
    error: string | null;
}

const state: AppState = reactive({
    user: api.currentUser,
    tournaments: [],
    teams: [],
    matches: [],
    isLoading: false,
    error: null,
});

export const appState = readonly(state);

export const mutations = {
    setUser(user: User | null) {
        state.user = user;
    },

    setTournaments(tournaments: Tournament[]) {
        state.tournaments = tournaments;
    },

    addTournament(tournament: Tournament) {
        state.tournaments.push(tournament);
    },

    updateTournament(updatedTournament: Tournament) {
        const index = state.tournaments.findIndex(t => t.id === updatedTournament.id);
        if (index !== -1) {
            state.tournaments[index] = updatedTournament;
        }
    },

    removeTournament(id: number) {
        state.tournaments = state.tournaments.filter(t => t.id !== id);
    },

    setTeams(teams: Team[]) {
        state.teams = teams;
    },

    addTeam(team: Team) {
        state.teams.push(team);
    },

    setMatches(matches: Match[]) {
        state.matches = matches;
    },

    addMatch(match: Match) {
        state.matches.push(match);
    },

    updateMatch(updatedMatch: Match) {
        const index = state.matches.findIndex(m => m.id === updatedMatch.id);
        if (index !== -1) {
            state.matches[index] = updatedMatch;
        }
    },

    setLoading(isLoading: boolean) {
        state.isLoading = isLoading;
    },

    setError(error: string | null) {
        state.error = error;
    },

    clearError() {
        state.error = null;
    },
};

export const actions = {
    async login(username: string, password: string) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const tokenResponse = await api.login({ username, password });
            api.setAuth(tokenResponse.access_token, { 
                username, 
                email: '', 
                is_active: true, 
                is_admin: false, 
                created_at: '',
                id: 0
            });

            const user = await api.getCurrentUser();
            mutations.setUser(user);
            return true;
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Login failed');
            return false;
        } finally {
            mutations.setLoading(false);
        }
    },

    async register(username: string, email: string, password: string, fullName?: string) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            await api.register({ username, email, password, full_name: fullName });
            return await this.login(username, password);
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Registration failed');
            return false;
        } finally {
            mutations.setLoading(false);
        }
    },

    logout() {
        api.clearAuth();
        mutations.setUser(null);
        mutations.setTournaments([]);
        mutations.setTeams([]);
        mutations.setMatches([]);
    },

    async loadTournaments(game?: string) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const tournaments = await api.getTournaments({ game });
            mutations.setTournaments(tournaments);
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to load tournaments');
        } finally {
            mutations.setLoading(false);
        }
    },

    async createTournament(tournamentData: any) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const tournament = await api.createTournament(tournamentData);
            mutations.addTournament(tournament);
            return tournament;
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to create tournament');
            throw error;
        } finally {
            mutations.setLoading(false);
        }
    },

    async loadTeams() {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const teams = await api.getTeams();
            mutations.setTeams(teams);
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to load teams');
        } finally {
            mutations.setLoading(false);
        }
    },

    async createTeam(teamData: any) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const team = await api.createTeam(teamData);
            mutations.addTeam(team);
            return team;
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to create team');
            throw error;
        } finally {
            mutations.setLoading(false);
        }
    },

    async registerTeamForTournament(tournamentId: number, teamId: number) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const participation = await api.registerForTournament(tournamentId, teamId);
            return participation;
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to register team');
            throw error;
        } finally {
            mutations.setLoading(false);
        }
    },

    async loadTournamentParticipants(tournamentId: number) {
        try {
            mutations.setLoading(true);
            mutations.clearError();

            const participants = await api.getTournamentParticipants(tournamentId);
            return participants;
        } catch (error: any) {
            mutations.setError(error.response?.data?.detail || 'Failed to load participants');
            throw error;
        } finally {
            mutations.setLoading(false);
        }
    },
};