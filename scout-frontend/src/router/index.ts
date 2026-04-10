import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '@/views/UploadView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: UploadView,
    },
    {
      path: '/review/:id',
      name: 'review',
      component: () => import('@/views/ReviewView.vue'),
      props: true,
    },
  ],
})

export default router
