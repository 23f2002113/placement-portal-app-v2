import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/login', name: 'login', component: Login },
    { path: '/register', name: 'register', component: Register },
    { 
      path: '/dashboard/admin', name: 'admin-dashboard', 
      component: AdminDashboard, 
      meta: { loginrequired: true, role: 'admin' } 
    },
    { 
      path: '/dashboard/student', name: 'student-dashboard', 
      component: StudentDashboard, 
      meta: { loginrequired: true, role: 'student' } 
    },
    { 
      path: '/dashboard/company', name: 'company-dashboard', 
      component: CompanyDashboard, 
      meta: { loginrequired: true, role: 'company' } 
    }
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')

  if (to.meta.loginrequired) {
    if (!token) {
      next({ name: 'login' })
    } 
    else if (to.meta.role && to.meta.role !== userRole) {
      next({ path: `/dashboard/${userRole}` }) 
    } 
    else {
      next()
    }
  } 
  else {
      next()
    }
})

export default router

