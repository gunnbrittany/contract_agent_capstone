import { useState, useCallback } from 'react';

export type PageType = 'intelligence' | 'mcp' | 'chat' | 'agents' | 'search';

export const useRouter = (initialPage: PageType = 'intelligence') => {
  const [currentPage, setCurrentPage] = useState<PageType>(initialPage);

  const navigate = useCallback((page: PageType) => {
    setCurrentPage(page);
  }, []);

  return {
    currentPage,
    navigate
  };
};
