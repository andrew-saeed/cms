import Alpine from 'alpinejs'
import flatpickr from 'flatpickr'
import Editor from '@toast-ui/editor'
import Cookies from 'js-cookie'

import 'flatpickr/dist/flatpickr.css'
import 'flatpickr/dist/themes/dark.css'
import '@toast-ui/editor/dist/toastui-editor.css'
import '@toast-ui/editor/dist/theme/toastui-editor-dark.css'

document.addEventListener('alpine:init', () => {

    Alpine.store('context', {})

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
        navLinksList: null,

        init() {
            this.navLinksList = document.querySelector('.links-list')
            this.navLinksList.style.maxHeight = '0px'
        },
        toggle() {
            if(this.navLinksList.style.maxHeight === '0px') {
                this.navLinksList.style.maxHeight = this.navLinksList.scrollHeight + 'px'
            } else {
                this.navLinksList.style.maxHeight = '0px'
            }
            this.open = !this.open
        }
    }))

    Alpine.data('chipsPicker', () => ({

        tags: [],
        tagsFull: false,
        tagsList: null,
        autoCompleteList: null,
        autoCompleteListItems: null,
        currentInput: null,

        init() {
            this.tagsList = this.$refs.tagsList
            this.autoCompleteList = this.$el.querySelector('.auto-complete-list')
            this.autoCompleteList.style.display = 'none'
            this.autoCompleteListItems = this.autoCompleteList.querySelectorAll('li')
            this.$store.context.chipsPicker = {
                id: this.$id('chipsPicker'),
                getAllTagsStr: () => this.getAllTagsStr(),
                loadPostTags: () => this.loadPostTags(),
                loadPostTag: () => this.loadPostTag()
            }
        },
        switchChipMode(chip) {

            this.tags.map(tag => {
                if(tag.id == chip.dataset.tagId) {
                    tag.value = chip.value
                    tag.mode = 'view'
                    this.currentInput = null
                }
                return tag
            })
            if(this.tags.length < 4) {
                this.tags.push({id: crypto.randomUUID(), value: '', mode: 'edit'})
                this.$nextTick(() => this.tagsList.querySelector('li:last-of-type input').focus())
            } else if(this.tags.length === 4) {
                this.tagsFull = true
            }
        },
        addNewTag() {
            this.autoCompleteList.style.display = 'none'
            
            if(this.$el.value.trim().length > 0) {

                this.switchChipMode(this.$el)
            }
        },
        removeTag(tagId) {
            this.tags = [...this.tags.filter(tag => tag.id !== tagId)]
            if(this.tagsFull) {
                this.tagsFull = false
                this.$nextTick(() => this.tags.push({id: crypto.randomUUID(), value: '', mode: 'edit'}))
            }
        },
        pickTag() {
            this.currentInput.value = this.$el.innerText
            this.switchChipMode(this.currentInput)
            this.autoCompleteList.style.display = 'none'
        },
        typing() {
            if(this.currentInput == null) this.currentInput = this.$el

            if(this.$el.value.length > 0) {

                this.autoCompleteList.style.display = 'block'

                for(let i = 0; i < this.autoCompleteListItems.length; i++) {

                    const txt = this.autoCompleteListItems[i].textContent.toLowerCase()
                    
                    if(txt.includes(this.$el.value)) {
                        this.autoCompleteListItems[i].style.display = ''
                    } else {
                        this.autoCompleteListItems[i].style.display = 'none'
                    }
                }
            }
        },
        getAllTagsStr() {
            const inputs = this.$refs.tagsList.querySelectorAll('li input')
            const allTagsStr = Array.from(inputs).map(input => input.value.trim()).filter(Boolean).join()
            return allTagsStr
        },
        loadPostTags() {
            const postTagsItem = this.$el.querySelectorAll('.current-post-tags li')
            for(let item of postTagsItem) {
                this.tags.push({id: crypto.randomUUID(), 
                    value: item.innerHTML, 
                    mode: 'view'})
            }
            if(postTagsItem.length < 4) this.tags.push({id: crypto.randomUUID(), value: '', mode: 'edit'})
            else if(postTagsItem.length == 4) this.tagsFull = true
        },
        loadPostTag() {
            this.tags.push({id: crypto.randomUUID(), value: '', mode: 'edit'})
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
            this.$nextTick(() => this.$store.context.chipsPicker.loadPostTag())
        },
        async post(action) {
            const allTagsStr = this.$store.context.chipsPicker.getAllTagsStr()
            const formData = new FormData()
            formData.append('action', action)
            formData.append('title', this.$refs.title.value)
            formData.append('body', this.editor.getMarkdown())
            formData.append('tags', allTagsStr)

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
            this.$nextTick(() => this.$store.context.chipsPicker.loadPostTags())

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
            const allTagsStr = this.$store.context.chipsPicker.getAllTagsStr()
            const formData = new FormData()
            formData.append('title', this.$refs.title.value)
            formData.append('body', this.editor.getMarkdown())
            formData.append('tags', allTagsStr)
            
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
        postsMainList: null,

        init() {
            this.postsMainList = this.$el.querySelector('ul.main-list')

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
            else this.postsMainList.insertAdjacentHTML('beforeend', html)
            this.isFetching = false
        }
    }))

    Alpine.data('likePost', () => ({

        postId: null,
        csrftoken: null,
        likeStatus: null,
        pending: null,
        totalLikes: 0,

        init(){
            this.postId = this.$el.dataset.postId
            this.csrftoken = Cookies.get('csrftoken')
            this.likeStatus = this.$el.dataset.isLiked === 'True' ? 'fill' : 'empty'
            this.totalLikes = parseInt(this.$el.dataset.totalLikes)
        },
        async toggle(action='') {

            if(this.pending) return

            this.pending = true

            const formData = new FormData()
            formData.append('id', this.postId)
            formData.append('action', action)

            const result = await fetch('/posts/like_post/', {
                method: 'POST',
                headers: {'X-CSRFToken': this.csrftoken},
                mode:'same-origin',
                body: formData
            })

            const res = await result.json()
            if(res.action == 'like') {
                this.likeStatus = 'fill'
                this.totalLikes += 1
            } else {
                this.likeStatus = 'empty'
                this.totalLikes -= 1
            }
            this.pending = false
        }
    }))
})

Alpine.start()