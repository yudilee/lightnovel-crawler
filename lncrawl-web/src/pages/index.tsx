import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { Reader } from '@/store/_reader';
import type { User } from '@/types';
import axios from 'axios';
import { useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  Navigate,
  RouterProvider,
  createBrowserRouter,
  type RouterState,
} from 'react-router-dom';
import { ADMIN_ROUTES, AUTH_ROUTES, USER_ROUTES } from './router';

export const App: React.FC<any> = () => {
  const loggedIn = useSelector(Auth.select.loggedIn);
  const adminUser = useSelector(Auth.select.isAdmin);

  useEffect(() => {
    const updateUser = async () => {
      try {
        const result = await axios.get<User>(`/api/auth/me`);
        store.dispatch(Auth.action.setUser(result.data));
      } catch {}
    };
    if (loggedIn) {
      updateUser();
    }
  }, [loggedIn]);

  const routes = useMemo(() => {
    if (!loggedIn) {
      return AUTH_ROUTES;
    }
    if (adminUser) {
      return ADMIN_ROUTES;
    }
    return USER_ROUTES;
  }, [loggedIn, adminUser]);

  const router = useMemo(
    () =>
      createBrowserRouter([
        ...routes,
        {
          path: '*',
          element: <Navigate to="/" replace />,
        },
      ]),
    [routes]
  );

  useEffect(() => {
    let previous: RouterState | undefined;
    return router.subscribe((state) => {
      try {
        const currPath = state.location.pathname;
        const prevPath = previous?.location.pathname;
        if (prevPath?.startsWith('/read') && !currPath.startsWith('/read')) {
          if (Reader.select.speaking(store.getState())) {
            store.dispatch(Reader.action.setSpeaking(false));
            store.dispatch(Reader.action.setSepakPosition(0));
          }
        }
      } catch (err) {
        console.error('Unexpected error in router subscriber', err);
      } finally {
        previous = state;
      }
    });
  }, [router]);

  return <RouterProvider router={router} />;
};
