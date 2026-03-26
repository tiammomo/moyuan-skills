import matter from 'gray-matter';

export function parseMarkdown(content: string): { content: string; data: Record<string, unknown> } {
  const { content: markdown, data } = matter(content);
  return { content: markdown, data };
}

export function extractHeadings(content: string): { title: string; level: number; id: string }[] {
  const headingRegex = /^(#{1,3})\s+(.+)$/gm;
  const headings: { title: string; level: number; id: string }[] = [];
  let match;

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const title = match[2].trim();
    const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    headings.push({ title, level, id });
  }

  return headings;
}

export function renderMarkdown(content: string): string {
  // Simple markdown rendering - in production, use remark/rehype
  let html = content;

  // Code blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers with IDs
  html = html.replace(/^### (.+)$/gm, (_, title) => {
    const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    return `<h3 id="${id}">${title}</h3>`;
  });
  html = html.replace(/^## (.+)$/gm, (_, title) => {
    const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    return `<h2 id="${id}">${title}</h2>`;
  });
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Lists
  html = html.replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/^\s*\*\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

  // Numbered lists
  html = html.replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Blockquotes
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr />');

  // Paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = '<p>' + html + '</p>';
  html = html.replace(/<p><(h[1-3]|ul|ol|pre|blockquote|hr)/g, '<$1');
  html = html.replace(/<\/(h[1-3]|ul|ol|pre|blockquote)><\/p>/g, '</$1>');
  html = html.replace(/<p>\s*<\/p>/g, '');

  // Tables (basic support)
  html = html.replace(/\|(.+)\|/g, (match) => {
    const cells = match.split('|').filter(Boolean);
    if (cells.some((c) => /^-+$/.test(c.trim()))) {
      return '';
    }
    const row = cells.map((c) => `<td>${c.trim()}</td>`).join('');
    return `<tr>${row}</tr>`;
  });

  return html;
}

function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
