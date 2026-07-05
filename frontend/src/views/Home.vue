<template>
  <div class="home">
    <section class="content1">
      <h1>Welcome to Placement Portal</h1>
      <p>Connecting Students, Companies, and Admin on one platform</p>
      
      <div class="buttons">
        <!-- Show Go to Dashboard if already logged in -->
        <router-link v-if="isAuthenticated" :to="'/dashboard/' + role" class="btn btn-primary">
          Go to Dashboard
        </router-link>

        <!-- Show Login & Register only if NOT logged in -->
        <router-link v-if="!isAuthenticated" to="/login" class="btn btn-primary">Login</router-link>
        <router-link v-if="!isAuthenticated" to="/register" class="btn btn-secondary">Register</router-link>
      </div>
    </section>

    <section class="content2">
      <div class="card btn btn-outline-light">
        <h3>For Students</h3>
        <p>Search jobs, apply with one click, track application status.</p>
      </div>
      
      <div class="card btn btn-outline-light">
        <h3>For Companies</h3>
        <p>Post jobs, review applicants, schedule interviews.</p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      isAuthenticated: false,
      role: ""
    }
  },
  methods: {
    checkSession() {
      const token = localStorage.getItem("token")
      const storedRole = localStorage.getItem("role")
      if (token && storedRole) {
        this.isAuthenticated = true
        this.role = storedRole
      } else {
        this.isAuthenticated = false
        this.role = ""
      }
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
.home {
  min-height: calc(100vh - 200px); 
  padding: 40px 5%;
}

.content1 {
  text-align: center;
  padding: 20px;
}

.content1 h1 {
  font-size: 36px;
  color: #07325e;
  margin-bottom: 16px;
}

.content1 p {
  font-size: 25px;
  color: #555;
  margin-bottom: 30px;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn {
  padding: 12px 28px;
  text-decoration: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  transition: 0.2s;
}

.btn-primary {
  background: #07325e;
  color: white;
}

.btn-secondary {
  background: white;
  color: #07325e;
  border: 2px solid #07325e;
}

.content2 {
  display: flex;
  justify-content: center;
  gap: 25px;
  margin-top: 60px;
  flex-wrap: wrap;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  width: 350px;
  text-align: center;
}

.card h3 {
  color: #07325e;
  margin-bottom: 10px;
  font-size: 25px;
}

.card p {
  color: #666;
  font-size: 20px;
  line-height: 1.5;
}
</style>