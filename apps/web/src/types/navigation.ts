export interface NavItem {
  label: string;
  href: string;
  available: boolean;
}

export interface NavSection {
  label: string;
  items: NavItem[];
}
