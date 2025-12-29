import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface User {
    id: number;
    username: string;
    email: string;
    full_name?: string;
    bio?: string;
    is_active: boolean;
    is_admin: boolean;
    created_at: string;
}

export interface Tournament {
    id: number;
    name: string;
    game: string;
    description?: string;
    max_teams: number;
    prize_pool: number;
    start_date?: string;
    end_date?: string;
    status: string;
    organizer_id: number;
    created_at: string;
}

export interface Team {
    id: number;
    name: string;
    tag?: string;
    description?: string;
    created_at: string;
}

export interface Match {
    id: number;
    tournament_id: number;
    round: number;
    team1_id: number;
    team2_id: number;
    score1: number;
    score2: number;
    winner_id?: number;
    match_date?: string;
    status: string;
}

export interface Participation {
    id: number;
    tournament_id: number;
    team_id: number;
    registered_at: string;
    final_position?: number;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData extends LoginCredentials {
    email: string;
    full_name?: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

class ApiClient {
    private token: string | null = null;
    private user: User | null = null;

    constructor() {
        // Load token from localStorage
        const savedToken = localStorage.getItem('auth_token');
        const savedUser = localStorage.getItem('user');
        
        if (savedToken) {
            this.token = savedToken;
        }
        
        if (savedUser) {
            this.user = JSON.parse(savedUser);
        }
    }

    private get headers() {
        const headers: any = {
            'Content-Type': 'application/json',
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    setAuth(token: string, user: User) {
        this.token = token;
        this.user = user;
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
    }

    get isAuthenticated(): boolean {
        return !!this.token;
    }

    get currentUser(): User | null {
        return this.user;
    }

    // Auth endpoints
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await axios.post(
            `${API_BASE_URL}/token`,
            formData,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );
        return response.data;
    }

    async register(data: RegisterData): Promise<User> {
        const response = await axios.post(
            `${API_BASE_URL}/register`,
            data,
            { headers: this.headers }
        );
        return response.data;
    }

    async getCurrentUser(): Promise<User> {
        const response = await axios.get(
            `${API_BASE_URL}/users/me`,
            { headers: this.headers }
        );
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(this.user));
        return response.data;
    }

    // Tournament endpoints
    async getTournaments(params?: {
        skip?: number;
        limit?: number;
        game?: string;
    }): Promise<Tournament[]> {
        const response = await axios.get(
            `${API_BASE_URL}/tournaments`,
            { 
                headers: this.headers,
                params 
            }
        );
        return response.data;
    }

    async getTournament(id: number): Promise<Tournament> {
        const response = await axios.get(
            `${API_BASE_URL}/tournaments/${id}`,
            { headers: this.headers }
        );
        return response.data;
    }

    async createTournament(tournament: Omit<Tournament, 'id' | 'status' | 'organizer_id' | 'created_at'>): Promise<Tournament> {
        const response = await axios.post(
            `${API_BASE_URL}/tournaments/`,
            tournament,
            { headers: this.headers }
        );
        return response.data;
    }

    async updateTournament(id: number, tournament: Partial<Tournament>): Promise<Tournament> {
        const response = await axios.put(
            `${API_BASE_URL}/tournaments/${id}`,
            tournament,
            { headers: this.headers }
        );
        return response.data;
    }

    async deleteTournament(id: number): Promise<void> {
        await axios.delete(
            `${API_BASE_URL}/tournaments/${id}`,
            { headers: this.headers }
        );
    }

    // Team endpoints
    async getTeams(params?: {
        skip?: number;
        limit?: number;
    }): Promise<Team[]> {
        const response = await axios.get(
            `${API_BASE_URL}/teams`,
            { 
                headers: this.headers,
                params 
            }
        );
        return response.data;
    }

    async createTeam(team: Omit<Team, 'id' | 'created_at'>): Promise<Team> {
        const response = await axios.post(
            `${API_BASE_URL}/teams/`,
            team,
            { headers: this.headers }
        );
        return response.data;
    }

    // Match endpoints
    async createMatch(match: Omit<Match, 'id' | 'status' | 'winner_id'>): Promise<Match> {
        const response = await axios.post(
            `${API_BASE_URL}/matches/`,
            match,
            { headers: this.headers }
        );
        return response.data;
    }

    async updateMatchScore(matchId: number, score1: number, score2: number): Promise<Match> {
        const response = await axios.put(
            `${API_BASE_URL}/matches/${matchId}/score`,
            null,
            { 
                headers: this.headers,
                params: { score1, score2 }
            }
        );
        return response.data;
    }

    // Participation endpoints
    async registerForTournament(tournamentId: number, teamId: number): Promise<Participation> {
        const response = await axios.post(
            `${API_BASE_URL}/participations/`,
            { tournament_id: tournamentId, team_id: teamId },
            { headers: this.headers }
        );
        return response.data;
    }

    async getTournamentParticipants(tournamentId: number): Promise<Participation[]> {
        const response = await axios.get(
            `${API_BASE_URL}/tournaments/${tournamentId}/participants`,
            { headers: this.headers }
        );
        return response.data;
    }
}

export const api = new ApiClient();