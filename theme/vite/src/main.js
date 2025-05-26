import Alpine from 'alpinejs'
import flatpickr from 'flatpickr'
import Editor from '@toast-ui/editor'
import Cookies from 'js-cookie'

import 'flatpickr/dist/flatpickr.css'
import 'flatpickr/dist/themes/dark.css'
import '@toast-ui/editor/dist/toastui-editor.css'
import '@toast-ui/editor/dist/theme/toastui-editor-dark.css'

document.addEventListener('alpine:init', () => {

    Alpine.data('removeEmptyHeader', () => ({
        init() {
            if(this.$el.innerText.length == 0) this.$el.remove()
        }
    }))

    Alpine.data('showToggler', () => ({

        open: false,

        toggle() {
            this.open = !this.open
        }
    }))

    Alpine.data('autofocusing', () => ({

        init() {
            this.$el.querySelector('input:not([type="hidden"])').focus()
        }
    }))

    Alpine.data('nav', () => ({

        open: false,

        init() {
            const navLinksList = document.querySelector('.links-list')
            navLinksList.style.maxHeight = '0px'
        },
        toggle() {
            if(navLinksList.style.maxHeight === '0px') {
                navLinksList.style.maxHeight = navLinksList.scrollHeight + 'px'
            } else {
                navLinksList.style.maxHeight = '0px'
            }
            this.open = !this.open
        }
    }))

    Alpine.data('profileForm', () => ({
        init() {

            flatpickr("#id_date_of_birth", {})

            this.$refs.photoInput.addEventListener('change', (e) => {
                const file = e.target.files[0]
                if(file) {
                    const reader = new FileReader()
                    reader.onload = (e) => {
                        this.$refs.photoImg.src = e.target.result
                    }
                    reader.readAsDataURL(file)
                }
            })
        },
        openPhotoImgInput() {
            this.$refs.photoInput.click()
        }
    }))

    Alpine.data('newPostForm', () => ({

        editor: null,
        csrftoken: null,

        init() {
            this.csrftoken = Cookies.get('csrftoken')

            this.editor = new Editor({
                el: this.$el.querySelector('#markdown-editor'),
                height: '31.25rem',
                initialEditType: 'markdown',
                previewStyle: 'tab',
                theme: 'dark',
                hideModeSwitch: true
            })
        },
        async post(action) {
            const formData = new FormData()
            formData.append('action', action)
            formData.append('title', this.$refs.title.value)
            formData.append('body', this.editor.getMarkdown())

            const res = await fetch('/posts/new', {
                method: 'POST',
                headers: {'X-CSRFToken': this.csrftoken},
                mode:'same-origin',
                body: formData
            })
            const data = await res.json()
            window.location.assign(data.url)
        }
    }))

    Alpine.data('updatePostForm', () => ({

        editor: null,
        id: null,
        csrftoken: null,

        init() {
            this.csrftoken = Cookies.get('csrftoken')

            this.id = this.$el.dataset.id
            const markdownEditor = this.$el.querySelector('#markdown-editor')
            this.editor = new Editor({
                el: markdownEditor,
                height: '31.25rem',
                initialEditType: 'markdown',
                previewStyle: 'tab',
                theme: 'dark',
                hideModeSwitch: true,
                initialValue: markdownEditor.textContent.trim()
            })
        },
        async update() {
            const formData = new FormData()
            formData.append('title', this.$refs.title.value)
            formData.append('body', this.editor.getMarkdown())
            const res = await fetch(`/posts/${this.id}/edit/`, {
                method: 'POST',
                headers: {'X-CSRFToken': this.csrftoken},
                mode:'same-origin',
                body: formData
            })
            const data = await res.json()
            window.location.assign(data.url)
        },
        cancel() {
            history.back();
        }
    }))

    Alpine.data('postsList', () => ({

        page:1,
        isFetching: false,
        emptyPage: false,

        init() {
            window.addEventListener('scroll', () => {
                const margin = document.body.clientHeight - window.innerHeight - 200
                if(window.scrollY > margin && !this.emptyPage && !this.isFetching) {
                    this.fetchPosts()
                }
            })
        },
        async fetchPosts() {
            this.page++
            this.isFetching = true
            const res = await fetch(`?list_paginated=1&page=${this.page}`)
            const html = await res.text()
            if(html == '') this.emptyPage = true
            this.$el.querySelector('ul.main-list').insertAdjacentHTML('beforeend', html)
            this.isFetching = false
        }
    }))
})

Alpine.start()