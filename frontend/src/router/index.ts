import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/problems',
      name: 'problems',
      component: () => import('../views/ProblemListView.vue'),
    },
    {
      path: '/problems/:category',
      name: 'problems-category',
      component: () => import('../views/ProblemListView.vue'),
    },
    {
      path: '/arena/:sessionId',
      name: 'arena',
      component: () => import('../views/CodingArenaView.vue'),
    },
    {
      path: '/interview/:sessionId',
      name: 'interview',
      component: () => import('../views/InterviewView.vue'),
    },
    {
      path: '/score/:sessionId',
      name: 'score',
      component: () => import('../views/ScoreView.vue'),
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
    },
  ],
})

export default router
