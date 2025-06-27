export type RoleType = '' | '*' | 'admin' | 'user';
export interface UserState {
  name?: string; // 确保这个属性存在
  avatar?: string;
  job?: string;
  organization?: string;
  location?: string;
  email?: string;
  introduction?: string;
  personalWebsite?: string;
  jobName?: string;
  organizationName?: string;
  locationName?: string;
  phone?: string;
  registrationDate?: string;
  accountId?: number;
  certification?: number;
  role: string;
}
