<template>
  <nav>
    <h2 v-if="isAuthenticated" class="welcome-text">Welcome, {{ name }} ({{ role }})</h2>
    <h2 v-else class="brand-text">Placement Portal</h2>

    <div class="nav-links">
      <router-link to="/">Home</router-link>
      
      <!-- Show these only if NOT logged in -->
      <router-link v-if="!isAuthenticated" to="/login">Login</router-link>
      <router-link v-if="!isAuthenticated" to="/register">Register</router-link>

      <!-- Show dynamic Dashboard link only if logged in -->
      <router-link v-if="isAuthenticated" :to="'/dashboard/' + role" class="dashboard-link">
        Dashboard
      </router-link>

      <!-- Show logout only if logged in -->
      <button v-if="isAuthenticated" @click="logout" class="logout-btn">Logout</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  data() {
    return {
      isAuthenticated: false,
      name: "",
      role: ""
    }
  },
  methods: {
    checkSession() {
      const token = localStorage.getItem("token")
      const storedRole = localStorage.getItem("role")
      if (token && storedRole) {
        this.isAuthenticated = true
        this.name = localStorage.getItem("name") || ""
        this.role = storedRole
      } else {
        this.isAuthenticated = false
        this.name = ""
        this.role = ""
      }
    },
    logout() {
      localStorage.clear()
      this.checkSession()
      this.$router.push("/login")
    }
  },
  created() {
    this.checkSession()
  },
  watch: {
    $route() {
      this.checkSession()
    }
  }
}
</script>

<style scoped>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 5%;
  background: #2c3e50;
  margin-top: 5px;
}

h2 {
  font-size: 30px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
}

.brand-text {
  color: white;
}

.welcome-text {
  color: #1abc9c;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
}

a {
  color: white;
  text-decoration: none;
  margin-left: 25px;
  font-size: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.dashboard-link {
  color: #1abc9c;
  font-weight: bold;
}

.logout-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 15px;
  margin-left: 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.logout-btn:hover {
  background: #c0392b;
}
</style>