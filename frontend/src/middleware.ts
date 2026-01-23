import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/upload',
  '/predict'
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
      const authObj = await auth();
      if (!authObj.userId) {
          return authObj.redirectToSignIn();
      }
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
