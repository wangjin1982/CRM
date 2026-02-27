/**
 * 表单验证规则
 */

export const required = (message = '此项为必填项') => {
  return (value: any) => {
    if (value === null || value === undefined || value === '') {
      return message
    }
    return true
  }
}

export const email = (message = '请输入有效的邮箱地址') => {
  return (value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return message
    }
    return true
  }
}

export const phone = (message = '请输入有效的手机号') => {
  return (value: string) => {
    const phoneRegex = /^1[3-9]\d{9}$/
    if (!phoneRegex.test(value)) {
      return message
    }
    return true
  }
}

export const minLength = (min: number, message?: string) => {
  return (value: string) => {
    if (value.length < min) {
      return message || `最少需要${min}个字符`
    }
    return true
  }
}

export const maxLength = (max: number, message?: string) => {
  return (value: string) => {
    if (value.length > max) {
      return message || `最多${max}个字符`
    }
    return true
  }
}
