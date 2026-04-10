<template>
  <Card>
    <CardHeader><CardTitle>Skills</CardTitle></CardHeader>
    <CardContent class="grid grid-cols-2 gap-4">
      <FormField name="skills.languages" v-slot="{ field }">
        <FormItem>
          <FormLabel>Programming Languages</FormLabel>
          <FormControl>
            <Input
              :model-value="Array.isArray(field.value) ? (field.value as string[]).join(', ') : ''"
              @update:model-value="(v: string) => field.onChange(v.split(',').map((s: string) => s.trim()).filter(Boolean))"
              placeholder="Python, TypeScript, Go"
            />
          </FormControl>
          <p class="text-xs text-muted-foreground">Comma-separated</p>
        </FormItem>
      </FormField>
      <FormField name="skills.frameworks" v-slot="{ field }">
        <FormItem>
          <FormLabel>Frameworks &amp; Libraries</FormLabel>
          <FormControl>
            <Input
              :model-value="Array.isArray(field.value) ? (field.value as string[]).join(', ') : ''"
              @update:model-value="(v: string) => field.onChange(v.split(',').map((s: string) => s.trim()).filter(Boolean))"
              placeholder="FastAPI, Vue 3, PyTorch"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="skills.tools" v-slot="{ field }">
        <FormItem>
          <FormLabel>Tools &amp; Platforms</FormLabel>
          <FormControl>
            <Input
              :model-value="Array.isArray(field.value) ? (field.value as string[]).join(', ') : ''"
              @update:model-value="(v: string) => field.onChange(v.split(',').map((s: string) => s.trim()).filter(Boolean))"
              placeholder="Docker, Git, PostgreSQL"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="skills.other" v-slot="{ field }">
        <FormItem>
          <FormLabel>Other</FormLabel>
          <FormControl>
            <Input
              :model-value="Array.isArray(field.value) ? (field.value as string[]).join(', ') : ''"
              @update:model-value="(v: string) => field.onChange(v.split(',').map((s: string) => s.trim()).filter(Boolean))"
              placeholder="Machine Learning, Mandarin, Technical Writing"
            />
          </FormControl>
        </FormItem>
      </FormField>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
</script>
