import numpy as np
from scipy import interpolate
import itertools
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import griddata
from scipy.interpolate import BarycentricInterpolator
from scipy import interpolate
from numpy import array, dot, mean, std, empty, argsort
from numpy.linalg import eigh, solve
from numpy.random import randn
from scipy.interpolate import griddata
from PIL import Image
import cv2
from scipy.spatial import ConvexHull
from matplotlib import path

from matplotlib.colors import Normalize
from matplotlib import cm

import matplotlib.pyplot as plt


class graphic_tools:
    _3DMM_obj = ()

    def __init__(self, _3dmm_obj):
        if _3dmm_obj is None:
            self._3DMM_obj = None
        else:
            self._3DMM_obj = _3dmm_obj

    def render3DMM(self, xIm, yIm, rgb, w, h):
        # need to perfomr the proj shape from the 3D model of the shape. The first column of projShape is xIm, the secondo is yIm.
        # The texture of the 3D model is the var rgb
        x_grid, y_grid = np.meshgrid([int(x) for x in range(w)], [int(y) for y in range(h)])
        _first_cord = np.transpose(xIm)
        _second_cord = np.transpose(yIm)
        # Interpolate z values on the grid
        coords = self._2linear_vects(_first_cord.reshape(_first_cord.shape[0],1), _second_cord.reshape(_second_cord.shape[0],1))
        Fr = LinearNDInterpolator(coords, np.transpose(rgb[:,0]))
        Fb = LinearNDInterpolator(coords, np.transpose(rgb[:,1]))
        Fg = LinearNDInterpolator(coords, np.transpose(rgb[:,2]))
        # Get values for each location
        imR = Fr(x_grid,y_grid)
        imG = Fb(x_grid,y_grid)
        imB = Fg(x_grid,y_grid)

        pts = np.column_stack([xIm, yIm])
        pts = np.round(pts)
        pts = np.unique(pts, axis=0)
        allPoints=np.column_stack((pts[:,0],pts[:,1]))
        hullPoints = ConvexHull(allPoints)
        bb = hullPoints.vertices
        bb = np.array(bb, dtype=np.intp)
        mask = self.inpolygon(x_grid, y_grid, pts[bb,0], pts[bb,1])
        mask = np.logical_not(mask)

        imR[mask] = 0
        imG[mask] = 0
        imB[mask] = 0
        # building image
        img = np.empty((imR.shape[0], imR.shape[1], 3))
        img[:,:,0] = imR
        img[:,:,1] = imG
        img[:,:,2] = imB
        #img = img*255
        return np.array(img,dtype=np.uint8)

    def inpolygon(self, xq, yq, xv, yv):
        shape = xq.shape
        xq = xq.reshape(-1)
        yq = yq.reshape(-1)
        xv = xv.reshape(-1)
        yv = yv.reshape(-1)
        q = [(xq[i], yq[i]) for i in range(xq.shape[0])]
        p = path.Path([(xv[i], yv[i]) for i in range(xv.shape[0])])
        return p.contains_points(q).reshape(shape)

    def resampleRGB(self,P,colors,step):
        min_x = np.amin(P[0,:], axis=0)
        max_x = np.amax(P[0,:], axis=0)
        min_y = np.amin(P[1,:], axis=0)
        max_y = np.amax(P[1,:], axis=0)
        Xsampling = np.arange(min_x, max_x, step, dtype='float')
        Ysampling = np.arange(max_y, min_y, -step, dtype='float')
        x, y = np.meshgrid(Xsampling, Ysampling)
        _first_cord = np.transpose(P[0,:])
        _second_cord = np.transpose(P[1,:])
        coords = self._2linear_vects(_first_cord.reshape(_first_cord.shape[0],1), _second_cord.reshape(_second_cord.shape[0],1))
        #Fr = griddata(coords, np.transpose(colors[0, :]), (x, y), method='linear')
        #Fg = griddata(coords, np.transpose(colors[1, :]), (x, y))
        #Fb = griddata(coords, np.transpose(colors[2, :]), (x, y))

        Fr = LinearNDInterpolator(coords, np.transpose(colors[0, :]))
        Fb = LinearNDInterpolator(coords, np.transpose(colors[1, :]))
        Fg = LinearNDInterpolator(coords, np.transpose(colors[2, :]))

        texR = Fr(x,y)
        texG = Fb(x,y)
        texB = Fg(x,y)
        #remove Nan elements
        mask = np.isnan(texR)
        index = np.array(mask, dtype=np.intp)
        texR[mask] = 0
        texG[mask] = 0
        texB[mask] = 0
        img = np.empty((texR.shape[0], texR.shape[1], 3))
        img[:,:,0] = texR
        img[:,:,1] = texG
        img[:,:,2] = texB
        return img, Xsampling, Ysampling

    def _2linear_vects(self, X,Y): # Creo le coordinate (X,Y) da passare alla funzione interpolatrice
        coords = np.empty((1, 2))
        for i in range(X.shape[0]):
            new_cord = np.array([X[i, 0], Y[i, 0]]).reshape(1, 2, order='F')
            coords = np.row_stack((coords, new_cord))
        coords = np.delete(coords, (0), axis=0)
        return coords

    def denseResampling(self, defShape, proj_shape, img, S, R, t, visIdx):
        grid_step = 1
        max_sh = (np.amax(proj_shape, axis=0))
        max_sh = np.reshape(max_sh,(1,2),order='F')
        min_sh = np.amin(proj_shape, axis=0)
        min_sh = np.reshape(min_sh, (1,2), order='F')
        Xsampling = np.arange(min_sh[0,0], max_sh[0,0], grid_step, dtype='float')
        Ysampling = np.arange(max_sh[0,1], min_sh[0,1], -grid_step, dtype='float')
        # round the float numbers
        Xsampling = np.around(Xsampling)
        Ysampling = np.around(Ysampling)

        print ("SAMPLING THE GRID")
        x_grid, y_grid = np.meshgrid(Xsampling, Ysampling)
        print ("3D LOCATION INTERPOLATION")
        index = np.array(visIdx, dtype=np.intp)
        X = proj_shape[index, 0]
        Y = proj_shape[index, 1]
        coords = self._2linear_vects(X,Y)
        #coords = list(zip(X,Y))
        Fx = LinearNDInterpolator(coords, defShape[index, 0])
        Fy = LinearNDInterpolator(coords, defShape[index, 1])
        Fz = LinearNDInterpolator(coords, defShape[index, 2])
        print ("PIXEL SAMPLING")
        x = Fx(x_grid.flatten(order='F'), y_grid.flatten(order='F'))
        y = Fy(x_grid.flatten(order='F'), y_grid.flatten(order='F'))
        z = Fz(x_grid.flatten(order='F'), y_grid.flatten(order='F'))
        print ("IMAGE BUILDING")
        x = x[~np.isnan(x).any(axis=1)]
        y = y[~np.isnan(y).any(axis=1)]
        z = z[~np.isnan(z).any(axis=1)]
        mod3d = np.dstack([x, y, z])
        #mod3d = np.delete(mod3d, [0,1,2,3], axis=0) # c'erano 3 valori in piu dall'interpolazione...??
        mod3d = np.reshape(mod3d,(mod3d.shape[0],3))
        print ("FINAL RENDERING")
        projMod3d = np.transpose(self._3DMM_obj.getProjectedVertex(mod3d, S, R, t))
        colors = self.getRGBtexture(np.round(projMod3d), img)
        colors = self._3DMM_obj.transVertex(colors)
        print ("DONE DENSE RESAMPLING")
        return [mod3d, colors]

    def getRGBtexture(self, coordTex, tex):
        R = (tex[:,:,0]).flatten(order='F')
        G = (tex[:,:,1]).flatten(order='F')
        B = (tex[:,:,2]).flatten(order='F')
        Xtex = np.round(coordTex[:,0])
        Ytex = np.round(coordTex[:,1])
        Xtex = np.maximum(Xtex, np.tile(1, Xtex.shape[0]))
        Ytex = np.maximum(Ytex, np.tile(1, Ytex.shape[0]))
        Xtex = np.minimum(Xtex, np.tile(tex.shape[1], Xtex.shape[0]))
        Ytex = np.minimum(Ytex, np.tile(tex.shape[0], Ytex.shape[0]))
        I = Ytex + (Xtex - 1) * tex.shape[0]
        I = I.astype(int)        
        Ri = R[I]
        Gi = G[I]
        Bi = B[I]
        colors = np.empty((Ri.shape[0],1))
        colors = np.hstack((colors, Ri.reshape(Ri.shape[0],1)))
        colors = np.hstack((colors, Gi.reshape(Gi.shape[0],1)))
        colors = np.hstack((colors, Bi.reshape(Bi.shape[0],1)))
        colors = np.delete(colors, (0), axis=1)
        colors = (colors.astype(float))/255.0

        return colors

    def renderFaceLossLess(self, defShape, projShape, img, S, R, T, renderingStep, visIdx):
        [mod3d, colors] = self.denseResampling(defShape, projShape, img, S, R, T, visIdx)  
        frontal_view = self.build_image(np.transpose(mod3d), np.transpose(defShape), colors, renderingStep)
        return frontal_view, colors, mod3d

    def build_image(self, P_f, P, colors, step):
        print("START BUILD FRONTAL VIEW")
        min_x = np.amin(P[0,:])
        max_x = np.amax(P[0,:])
        min_y = np.amin(P[1,:])
        max_y = np.amax(P[1,:])
        Xsampling = np.arange(min_x, max_x, step, dtype='float')
        Ysampling = np.arange(max_y, min_y, -step, dtype='float')

        [x, y] = np.meshgrid(Xsampling, Ysampling)
        _first_cord = np.transpose(P_f[0,:])
        _second_cord = np.transpose(P_f[1,:])

        coords = self._2linear_vects(_first_cord.reshape(_first_cord.shape[0],1), _second_cord.reshape(_second_cord.shape[0],1))
        Fr = LinearNDInterpolator(coords, np.transpose(colors[0,:]))
        Fb = LinearNDInterpolator(coords, np.transpose(colors[1,:]))
        Fg = LinearNDInterpolator(coords, np.transpose(colors[2,:]))
        texR = np.nan_to_num(Fr(x, y))
        texG = np.nan_to_num(Fg(x, y))
        texB = np.nan_to_num(Fb(x, y))
        
        img = np.empty((texR.shape[0],texR.shape[1],3))
        img[:,:,0] = texR
        img[:,:,1] = texG
        img[:,:,2] = texB
        img = img*255
        print("DONE")
        return np.array(img,dtype=np.uint8)

    def resize_imgs(self, img, size_row, size_col):
        rows = img.shape[0]
        cols = img.shape[1]
        # resize the rows
        if rows > size_row:
            diff = rows - size_row
            for i in range(diff):
                img = np.delete(img, (i), axis=0)
        else:
            diff = size_row - rows
            new_row = np.zeros((1, cols, 3))
            for i in range(diff):
                img = np.vstack([img, new_row])
        if cols > size_col:
            diff = cols - size_col
            for i in range(diff):
                img = np.delete(img, (i), axis=1)
        else:
            diff = size_col - cols
            new_col = np.zeros((img.shape[0],1, 3))
        
            for i in range(diff):
                img = np.hstack([img,new_col])
        return img

   

    def avgModel(self, object):
        rows = object[0].frontalView.shape[0]
        cols = object[0].frontalView.shape[1]
        R_cumulative_matrix = object[0].frontalView[:, :, 0]
        G_cumulative_matrix = object[0].frontalView[:, :, 1]
        B_cumulative_matrix = object[0].frontalView[:, :, 2]
        for i in range(len(object)):
            current_R = object[i].frontalView[:, :, 0]
            current_G = object[i].frontalView[:, :, 1]
            current_B = object[i].frontalView[:, :, 2]
            R_cumulative_matrix = R_cumulative_matrix + current_R
            G_cumulative_matrix = G_cumulative_matrix + current_G
            B_cumulative_matrix = B_cumulative_matrix + current_B
        mean_R = R_cumulative_matrix / len(object)
        mean_G = G_cumulative_matrix / len(object)
        mean_B = B_cumulative_matrix / len(object)
        avgModel = np.empty((rows, cols, 3))
        avgModel[:,:,0] = mean_R
        avgModel[:,:,1] = mean_G
        avgModel[:,:,2] = mean_B

        return np.array(avgModel,dtype=np.uint8)

    def colors_AVG(self, object):
        cumulative_matrix_col = object[0].colors
        for i in range(len(object)):
            cumulative_matrix_col = cumulative_matrix_col + object[i].colors
        return cumulative_matrix_col/len(object)

    def deform_texture_fast(self, mean, eigenves, alpha, ex_to_ne):
        dim = eigenves.shape[0]/3
        alpha_full = np.tile(np.transpose(alpha), (eigenves.shape[0],1))
        tmp_eigen = alpha_full*eigenves
        sumVec = tmp_eigen.sum(axis=1)
        sumVec = sumVec.reshape((sumVec.shape[0],1), order='F')
        sumMat = np.reshape(np.transpose(sumVec), (3,dim), order='F')
        return mean + sumMat

    def cov(self,X):
        """
        Covariance matrix
        note: specifically for mean-centered data
        note: numpy's `cov` uses N-1 as normalization
        """
        return dot(X.T, X) / X.shape[0]
        

    def pca(self,data, pc_count=None):
        """
        Principal component analysis using eigenvalues
        note: this mean-centers and auto-scales the data (in-place)
        """
        data -= mean(data, 0)
        data /= std(data, 0)
        C = self.cov(data)
        E, V = eigh(C)
        key = argsort(E)[::-1][:pc_count]
        E, V = E[key], V[:, key]
        U = dot(data, V)  # used to be dot(V.T, data.T).T
        return U, E, V

    def PIL2array(self,img):
        return np.array(img.getdata(),
                           np.uint8).reshape(img.size[1], img.size[0], 3)

    def mse(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        
        return err

    def compare_imgs(self,i1,i2):
        pairs = zip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
            # for gray-scale jpegs
            dif = sum(abs(p1 - p2) for p1, p2 in pairs)
        else:
            dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

        ncomponents = i1.size[0] * i1.size[1] * 3
        return (dif / 255.0 * 100) / ncomponents

    def mean(self, obj):
        sum = 0
        for i in range(len(obj)):
            sum += obj[i].ssim_D
        return sum/len(obj)

 
