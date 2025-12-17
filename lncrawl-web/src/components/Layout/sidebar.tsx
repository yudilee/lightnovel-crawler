import { Auth } from '@/store/_auth';
import { Menu } from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { buildMenu } from './menu';

export const MainLayoutSidebar: React.FC<any> = () => {
  const location = useLocation();
  const isAdmin = useSelector(Auth.select.isAdmin);

  const items = useMemo(
    () => buildMenu({ isAdmin, currentPath: location.pathname }),
    [isAdmin, location.pathname]
  );

  return (
    <Menu
      mode="inline"
      items={items}
      inlineIndent={15}
      defaultOpenKeys={[
        'admin', // keep open by default
      ]}
      style={{
        height: '100%',
      }}
    />
  );
};
