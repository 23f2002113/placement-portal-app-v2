<template>
  <nav class="navbar navbar-expand-lg navbar-dark  py-3 px-5 mb-4 shadow-sm">
    <div class="container-fluid d-flex justify-content-between align-items-center">
      
      <h2 v-if="isAuthenticated" class="navbar-brand m-0 text-success" >
        Welcome, {{ name }} ({{ role }})
      </h2>
      <h2 v-else class="navbar-brand m-0 text-white" >
        Placement Portal
      </h2>


      <div class="d-flex align-items-center gap-3">
        <router-link to="/" class="nav-link text-white mr-3">Home</router-link>
        
        <!-- Show only if NOT logged in -->
        <router-link v-if="!isAuthenticated" to="/login" class="nav-link text-white mr-3">Login</router-link>
        <router-link v-if="!isAuthenticated" to="/register" class="nav-link text-white">Register</router-link>

        <!-- Show only if logged in -->
        <button v-if="isAuthenticated" @click="logout" class="btn btn-danger btn-sm ml-3">Logout</button>
      </div>


      <form v-if="isAuthenticated && role === 'admin'" class="d-flex align-items-center" @submit.prevent="onSearch">
        <input 
          class="form-control mr-2 form-control-sm" type="search" placeholder="Search" v-model="searchQuery" required
        >
        <select class="form-control mr-2 form-control-sm" v-model="searchKey" required>
          <option value="" disabled selected>select</option>
          <option value="student">Student</option>
          <option value="company">Company</option>
        </select>

        <button class="btn btn-outline-success btn-sm" type="submit">Search</button>
      </form>

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
      role: "",
      searchQuery: "",
      searchKey: ""
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
      } 
      else {
        this.isAuthenticated = false
        this.name = ""
        this.role = ""
      }
    },
    logout() {
      localStorage.clear()
      this.checkSession()
      this.$router.push("/login")
    },
    onSearch() {
      if (!this.searchQuery.trim() || !this.searchKey) return

      // Redirects to Admin Dashboard with reactive search parameters
      this.$router.push({
        path: "/dashboard/admin",
        query: { 
          key: this.searchKey, 
          q: this.searchQuery,
          t: Date.now() 
        }
      })
      this.searchQuery = "" 
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
    background: #04172b;
    margin-top: 5px;
}

h2 {
    font-size: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
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

</style>

