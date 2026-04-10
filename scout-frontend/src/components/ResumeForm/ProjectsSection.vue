<template>
  <Card>
    <CardHeader><CardTitle>Projects</CardTitle></CardHeader>
    <CardContent class="space-y-4">
      <div v-for="(entry, idx) in fields" :key="entry.key" class="border rounded-lg p-4 space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <FormField :name="`projects[${idx}].name`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`projects[${idx}].url`" v-slot="{ field }">
            <FormItem>
              <FormLabel>URL</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" type="url" />
              </FormControl>
            </FormItem>
          </FormField>
        </div>
        <FormField :name="`projects[${idx}].description`" v-slot="{ field }">
          <FormItem>
            <FormLabel>Description</FormLabel>
            <FormControl>
              <Textarea :model-value="field.value as string" @update:model-value="field.onChange" :rows="2" />
            </FormControl>
          </FormItem>
        </FormField>
        <FormField :name="`projects[${idx}].technologies`" v-slot="{ field }">
          <FormItem>
            <FormLabel>Technologies <span class="text-muted-foreground text-xs">(comma-separated)</span></FormLabel>
            <FormControl>
              <Input
                :model-value="Array.isArray(field.value) ? (field.value as string[]).join(', ') : ''"
                @update:model-value="(v: string) => field.onChange(v.split(',').map((s: string) => s.trim()).filter(Boolean))"
              />
            </FormControl>
          </FormItem>
        </FormField>
        <FormField :name="`projects[${idx}].bullets`" v-slot="{ field }">
          <FormItem>
            <FormLabel>Highlights <span class="text-muted-foreground text-xs">(one per line)</span></FormLabel>
            <FormControl>
              <Textarea
                :model-value="Array.isArray(field.value) ? (field.value as string[]).join('\n') : ''"
                @update:model-value="(v: string) => field.onChange(v.split('\n').filter((l: string) => l.trim()))"
                :rows="3"
              />
            </FormControl>
          </FormItem>
        </FormField>
      </div>
      <p v-if="fields.length === 0" class="text-sm text-muted-foreground text-center py-4">No projects parsed.</p>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { useFieldArray } from 'vee-validate'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
// D-07: only 'fields' exposed — no push, remove, swap operations available to user
const { fields } = useFieldArray('projects')
</script>
