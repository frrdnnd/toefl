<template>
  <div class="min-h-screen bg-[#F5F9FF] flex text-slate-800">
    <Sidebar />

    <div class="flex-1 ml-0 lg:ml-72 min-h-screen">
      <Navbar />

      <main class="p-4 md:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Navbar from '@/components/Navbar.vue'
</script>