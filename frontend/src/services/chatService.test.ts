import { describe, it, expect, vi } from 'vitest'
import { chatService } from './chatService'

describe('ChatService', () => {
  describe('createStreamingChat error handling', () => {
    it('should handle Error instances correctly', async () => {
      const onChunk = vi.fn()
      const onComplete = vi.fn()
      const onError = vi.fn()

      // Mock fetch to reject with an Error instance
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

      await chatService.createStreamingChat(
        'test message',
        [],
        {},
        onChunk,
        onComplete,
        onError
      )

      expect(onError).toHaveBeenCalledWith(expect.any(Error))
      expect(onError).toHaveBeenCalledWith(expect.objectContaining({
        message: 'Network error'
      }))
    })

    it('should handle non-Error types by converting to Error', async () => {
      const onChunk = vi.fn()
      const onComplete = vi.fn()
      const onError = vi.fn()

      // Mock fetch to reject with a string
      global.fetch = vi.fn().mockRejectedValue('String error')

      await chatService.createStreamingChat(
        'test message',
        [],
        {},
        onChunk,
        onComplete,
        onError
      )

      expect(onError).toHaveBeenCalledWith(expect.any(Error))
      expect(onError).toHaveBeenCalledWith(expect.objectContaining({
        message: 'String error'
      }))
    })

    it('should handle unknown error types by converting to Error', async () => {
      const onChunk = vi.fn()
      const onComplete = vi.fn()
      const onError = vi.fn()

      // Mock fetch to reject with an object
      global.fetch = vi.fn().mockRejectedValue({ code: 500, details: 'Server error' })

      await chatService.createStreamingChat(
        'test message',
        [],
        {},
        onChunk,
        onComplete,
        onError
      )

      expect(onError).toHaveBeenCalledWith(expect.any(Error))
      expect(onError).toHaveBeenCalledWith(expect.objectContaining({
        message: '[object Object]'
      }))
    })
  })
})