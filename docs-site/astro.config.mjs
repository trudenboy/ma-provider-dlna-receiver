// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://trudenboy.github.io/ma-provider-dlna-receiver',
	base: '/ma-provider-dlna-receiver',
	integrations: [
		starlight({
			title: 'DLNA Receiver · MA Provider',
			editLink: {
				baseUrl: 'https://github.com/trudenboy/ma-provider-dlna-receiver/edit/dev/docs-site/src/content/docs/',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/trudenboy/ma-provider-dlna-receiver' },
			],
			sidebar: [
				{ label: 'Home', slug: 'index' },
				{ label: 'Configuration', slug: 'configuration' },
				{ label: 'Features', autogenerate: { directory: 'features' } },
				{ label: 'Development', items: [
					{ label: 'Dev Environment', slug: 'development' },
					{ label: 'Docker', slug: 'dev-docker' },
					{ label: 'Testing', slug: 'testing' },
					{ label: 'Contributing', slug: 'contributing' },
					{ label: 'Incident Management', slug: 'incident-management' },
				] },
			],
		}),
	],
});
